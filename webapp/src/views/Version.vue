<script setup lang="ts">
import Header from '@/components/Header.vue';
import { VersionsIndex } from '@/model/VersionsIndex';
import { standards } from '@/model/standards';
import { useAsyncState } from '@vueuse/core';
import { computed, ref } from 'vue';
import { useRoute } from 'vue-router';
import Version from '@/model/Version';
import type ImageReport from '@/model/ImageReport';
import { timeAgo } from '@/model/util';
import { sortFields } from '@/model/ImageReport';
import { orderBy } from 'lodash-es';
import quote from 'shell-quote/quote'

const route = useRoute()
const standardName = computed(() => route.params.name as string)
const tag = computed(() => route.params.tag as string)

const standard = computed(() => {
  return standards.find(s => s.name == standardName.value)
})

const versionLoader = useAsyncState(
  async () => {
    const index = await VersionsIndex.get()
    const ref = index.allVersionRefs.find(ref => ref.name == standardName.value && ref.tag == tag.value)
    if (!ref) throw new Error('Not found')
    const version = await Version.getWithFilename(ref.filename)
    selectedImage.value = version.images[0]
    return version
  },
  null,
)
const version = versionLoader.state
const selectedImage = ref<{arch: string, report: ImageReport} | null>(null)

const pythonsTable = computed(() => {
  if (!version.value) return null
  let pythonEnvironments = version.value.images[0].report.pythonEnvironments

  pythonEnvironments = orderBy(
    pythonEnvironments,
    ['identifierInfo.interpreter', 'identifierInfo.major', 'identifierInfo.minor', 'identifierInfo.variant'],
    ['asc', 'desc', 'desc', 'asc']
  )

  let pythonFields = version.value.fields.filter(f => f.id.startsWith('python.')) ?? []
  pythonFields = sortFields(pythonFields)
  const pythonIds = pythonEnvironments.map(p => p.identifier)
  const subfieldIds = new Set(pythonFields.map(f => f.id.split('.').slice(2).join('.')))
  const headers = ['Python', 'Version', 'Path', ...subfieldIds]
  const rows = [] as string[][]

  for (const pythonEnvironment of pythonEnvironments) {
    const prettyName = pythonEnvironment.prettyName.name + (pythonEnvironment.prettyName.variant ?? '')
    const row = [prettyName, pythonEnvironment.pythonVersion, `<code>${pythonEnvironment.path}</code>`] as string[]
    for (const subfieldId of subfieldIds) {
      const field = pythonFields.find(f => f.id == `python.${pythonEnvironment.identifier}.${subfieldId}`)
      row.push(field?.value ?? '')
    }
    rows.push(row)
  }

  return { headers, rows }
})

</script>

<template>
  <div v-if="versionLoader.isLoading.value" class="loading"></div>
  <div v-else-if="versionLoader.error.value" class="error">{{ versionLoader.error }}</div>
  <div v-else-if="version" class="version">
    <Header />

    <div class="spacer" style="height: 60px;"></div>

    <div class="margins">
      <h2>
        {{ standardName }}:{{ tag }}
      </h2>

      <h3>Metadata</h3>

      <dl>
        <dt>Standard</dt>
        <dd>
          <router-link :to="{name: 'standard', params: {name: standardName}}">
            {{ standardName }}
          </router-link>
        </dd>
        <dt>Created</dt>
        <dd>
          {{ version.date.toLocaleDateString(undefined, {dateStyle: 'full'}) }}
          ({{ timeAgo(version.date) }})
        </dd>
        <dt>Github commit</dt>
        <dd>
          <a :href="`https://github.com/pypa/manylinux/commit/${version.commit}`">
            <code>{{ version.commit }}</code>
          </a>
          &nbsp;
          <a :href="`https://github.com/pypa/manylinux/tree/${version.commit}`">
            Browse files
          </a>

        </dd>
      </dl>
      <h3>Images</h3>
      <table>
        <thead>
          <tr>
            <th>Arch</th>
            <th>URL</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="image in version.images">
            <td>{{ image.arch }}</td>
            <td><code>{{ image.report.metadata.image }}</code></td>
          </tr>
        </tbody>
      </table>

      <h3>OS</h3>
      <dl>
        <template v-for="field in version.fields.filter(f => f.id.startsWith('os'))">
          <dt>{{ field.label }}</dt>
          <dd>{{ field.value }}</dd>
        </template>
      </dl>

      <h3>Global tools</h3>
      <dl>
        <template v-for="field in version.fields.filter(f => f.id.startsWith('global-tools.'))">
          <dt>{{ field.label }}</dt>
          <dd>{{ field.value }}</dd>
        </template>
      </dl>

      <h3>Python environments</h3>
      <table class="python-envs">
        <thead>
          <tr>
            <th v-for="header in pythonsTable?.headers">{{header}}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in pythonsTable?.rows">
            <td v-for="value in row" v-html="value"></td>
          </tr>
        </tbody>
      </table>

      <div class="log">
        <div class="log-header">
          <h3 class="log-title">Inspection logs</h3>
          <div class="spacer" style="flex: 1"></div>
          <div class="log-tabs">
            <div class="tab" v-for="image in version.images"
                 :class="{selected: selectedImage?.arch == image.arch}"
                 @click="selectedImage = image"
                 role="tab">
              {{ image.arch }}
            </div>
          </div>
        </div>
        <div class="log-contents">
          <div class="log-entry"
               v-for="entry in selectedImage?.report.reportJSON.data.log"
               :class="{success: entry.return_code == 0}">
            <div class="command">$ {{ quote(entry.command) }}</div>
            <div class="stdout">{{ entry.stdout }}</div>
            <div class="stderr">{{ entry.stderr }}</div>
            <div class="return-code">{{ entry.return_code }}</div>
          </div>
        </div>
      </div>

      <div class="spacer" style="height: 30px"></div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.cards {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
h3 {
  margin-top: 20px;
}
:deep(code) {
  font-size: 0.9em;
  background-color: rgba(0, 0, 0, 0.05);
  padding: 1px 4px;
}
table {
  font-size: 0.95em;
}
table {
  display: block;
  overflow-x: auto;
  width: max-content;
  max-width: 100%;

  text-align: left;
  padding: 0;
  border-collapse: collapse;
  margin-bottom: 10px;
}
.python-envs {
  white-space: nowrap;
}
th, td {
  margin: 0;
  padding: 3px 14px;
  padding-left: 0;
  background: white;
}
th {
  font-weight: 500;
  border-bottom: 2px solid #DBDBDB;
  font-weight: 600;
}
td:first-child {
  white-space: nowrap;
}

dl {
  display: grid;
  grid-template-columns: auto auto;
  width: max-content;
  max-width: 100%;
  gap: 1px 14px;
}
dt {
  font-weight: 600;
  // margin-right: 10px;
  text-align: right;
}

.log-header {
  background-color: white;
  position: sticky;
  top: 0;
}
.log-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 14px;
  font-weight: 500;
  &::before {
    content: "";
    position: absolute;

    bottom: 0;
    left: 0;
    right: 0;
    height: 1px;
    background-color: #DBDBDB;
  }
  .tab {
    position: relative;
    padding: 5px 10px;
    cursor: pointer;
    &.selected {
      background-color: rgba(0, 0, 0, 0.05);
    }
  }
}
.log {
  .log-contents {
    background-color: rgba(0, 0, 0, 0.05);
    padding: 10px 15px;
    border-radius: 5px;
    margin-bottom: 10px;
    font-family: ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Consolas, 'DejaVu Sans Mono', monospace;
    font-weight: 400;
    font-size: 13px;
    overflow-x: auto;
  }
  .command {
    font-weight: 600;
  }
  .stdout, .stderr {
    white-space: pre-wrap;
      color: #a55;
  }
  .stderr {
    font-style: italic;
  }
  .return-code {
    font-weight: 600;
    color: #a55;
    text-align: right;
  }
  .log-entry.success {
    .return-code {
      visibility: hidden;
    }
    .stdout, .stderr {
      color: inherit;
    }
  }
}
</style>
