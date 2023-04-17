<script setup lang="ts">
import Version from '@/model/Version';
import { VersionsIndex, type VersionRef } from '@/model/VersionsIndex';
import { computedAsync, useAsyncState } from '@vueuse/core';
import { computed, reactive, ref, toRaw, watch, watchEffect } from 'vue';
import Header from '@/components/Header.vue';
import { fill, last, sortBy } from 'lodash';
import FixedHorizontalStickyVertical from '@/components/FixedHorizontalStickyVertical.vue';
import { regexExtract } from '@/model/util';
import { useRoute, useRouter } from 'vue-router';
import { compareStandardNames } from '@/model/standards';
import { sortFields } from '@/model/ImageReport';


const indexLoader = useAsyncState(
  VersionsIndex.get(),
  null,
)

const router = useRouter()
const route = useRoute()
const searchTerm = computed({
  get: () => {
    const query = route.query as { q?: string }
    return query.q ?? 'latest'
  },
  set: (value) => {
    router.replace({ query: { q: value }})
  }
})

const versionRefs = computed(() => {
  const index = indexLoader.state.value
  if (!index) {
    return []
  }
  const refs = index.search(searchTerm.value)
  refs.sort((a, b) => {
    const compareNameResult = compareStandardNames(a.name, b.name)
    if (compareNameResult !== 0) {
      return compareNameResult
    }
    return b.tag.localeCompare(a.tag)
  })
  return refs
})

interface VersionLoader {
  ref: VersionRef,
  version: Version|null,
  abortController: AbortController,
}
const versionCache = reactive<{[filename: string]: VersionLoader|undefined}>({})

const versionLoaders = ref<VersionLoader[]>([])
watch(versionRefs, versionRefs => {
  const newVersions: VersionLoader[] = []
  for (const versionRef of versionRefs) {
    let versionCacheItem = versionCache[versionRef.filename]
    if (!versionCacheItem) {
      versionCacheItem = reactive({
        ref: versionRef,
        version: null,
        abortController: new AbortController(),
      })

      Version.getWithFilename(versionRef.filename, versionCacheItem.abortController.signal)
        .then(version => { versionCacheItem!.version = version })
        .catch(error => {
          if (error.name !== 'AbortError') {
            console.error('failed to load version', error)
          }
        })
    }

    versionCache[versionRef.filename] = versionCacheItem
    newVersions.push(versionCacheItem)
  }
  versionLoaders.value = newVersions
})

watch(versionLoaders, (newState, oldState) => {
  newState = toRaw(newState)
  oldState = toRaw(oldState)
  for (const versionCacheItem of oldState) {
    if (!newState.includes(versionCacheItem)) {
      if (versionCacheItem.version == null) {
        versionCacheItem.abortController.abort()
        delete versionCache[versionCacheItem.ref.filename]
      }
    }
  }
})

const expandedFieldIds = reactive(new Set<string>())

interface FieldDescriptor {
  id: string
  label: string
  hasParent: boolean
  hasChildren: boolean
  isExpanded: boolean
  isVisible: boolean
  level: number
}
const fieldsById = computed(() => {
  const result = new Map<string, FieldDescriptor>()

  for (const versionCacheItem of versionLoaders.value) {
    if (versionCacheItem.version) {
      for (const field of versionCacheItem.version.fields) {
        if (!result.has(field.id)) {
          result.set(field.id, {
            id: field.id,
            label: field.label,
            hasParent: false,
            hasChildren: false,
            isExpanded: expandedFieldIds.has(field.id),
            isVisible: true,
            level: 0,
          })
        }
      }
    }
  }

  for (const fieldDescriptor of result.values()) {
    let parent = result.get(getParentId(fieldDescriptor.id) ?? '')
    if (!parent) continue

    fieldDescriptor.hasParent = true

    while (parent) {
      fieldDescriptor.level += 1

      parent.hasChildren = true
      if (!parent.isExpanded) {
        fieldDescriptor.isVisible = false
      }
      parent = result.get(getParentId(parent.id) ?? '')
    }
  }

  return result
})

const fields = computed(() => {
  return sortFields(Array.from(fieldsById.value.values()))
})

function getParentId(fieldId: string): string | null {
  const lastDotI = fieldId.lastIndexOf('.')
  if (lastDotI < 0) {
    return null
  }

  return fieldId.slice(0, lastDotI)
}

function getFieldValue(fieldId: string, version: Version) {
  return version.fields.find(f => f.id == fieldId)?.value
}

function rowClicked(event: MouseEvent, field: FieldDescriptor) {
  if (!field.hasChildren) return
  event.preventDefault()
  event.stopPropagation()

  if (expandedFieldIds.has(field.id)) {
    expandedFieldIds.delete(field.id)
  } else {
    expandedFieldIds.add(field.id)
  }
}

</script>

<template>
  <Header page="grid" />

  <div class="grid">
    <fixed-horizontal-sticky-vertical :height="35" :z-index="10" :sticky-top="0">
      <div class="search-bar">
        <img class="icon" src="@/assets/search-menu-icon.svg" alt="search-menu" role="button" />
        <input type="text" placeholder="all" v-model="searchTerm" />
      </div>
    </fixed-horizontal-sticky-vertical>
    <table cellspacing="0">
      <thead>
        <tr>
          <th></th>
          <th v-for="version in versionLoaders" :key="version.ref.filename">
            <router-link :to="{
              name: 'version',
              params: {name: version.ref.name, tag: version.ref.tag}
            }">
              {{ version.ref.name }}:<br>
              {{ version.ref.tag }}
            </router-link>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="field in fields"
            :class="{parent: field.hasChildren,
                     expanded: field.isExpanded,
                     hidden: !field.isVisible,
                     [`level-${field.level}`]: true}"
            @click="rowClicked($event, field)">
          <td>
            <span class="name" v-html="field.label"></span>
          </td>
          <td v-for="version in versionLoaders" :key="version.ref.filename">
            {{ version.version ? getFieldValue(field.id, version.version) : '' }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style lang="scss" scoped>
.grid {
  font-size: 14px;
}
.search-bar {
  background-color: black;
  padding: 0 36px;

  display: flex;
  gap: 10px;
  height: 35px;

  .icon {
    width: 21px;
    height: auto;
  }
  input[type="text"] {
    flex: 1;

    border: none;
    background: none;
    line-height: 35px;

    color: white;
    font-size: 14px;
    text-align: left;
    padding: 0;
    outline: none;
  }
}
table {
  padding: 0;
  text-align: left;
}
tbody {
  vertical-align: top;
}
th, td {
  margin: 0;
  padding: 2px;
  background: white;
  max-width: 230px;
}
th {
  white-space: nowrap;
  font-weight: 500;
  position: sticky;
  top: 35px;
  z-index: 1;
  background: white;
  border-bottom: 2px solid #DBDBDB;
  // box-shadow: 0 2px 2px -1px rgba(0, 0, 0, 0.4);

  font-weight: 600;
  padding: 9px 8px;

  a:link, a:visited {
    color: inherit;
  }
}
td:first-child, th:first-child {
  position: sticky;
  left: 0;
  z-index: 1;
  background: white;
  white-space: nowrap;
}
th:first-child {
  z-index: 2;
}
tr.hidden {
  visibility: collapse;
}

:global(body.is-safari .grid table tr.hidden) {
  // Safari doesn't support visibility: collapse, so we hide the row
  display: none;
}
tr.parent {
  td {
    border-top: 1px solid #DBDBDB;
  }
  position: relative;

  td {
    padding: 16px 8px;
  }

  td:first-child {
    padding-left: 27px;
    :deep(.variant) {
      font-size: 9px;
      font-weight: bold;
      font-style: italic;
    }
  }

  td:first-child::after {
    content: '';
    display: inline-block;
    width: 13px;
    height: 13px;
    background-image: url(@/assets/disclosure-triangle.svg);
    background-position: center;
    background-repeat: no-repeat;
    position: absolute;
    left: 9px;
    top: 18px;
  }
  &.expanded td:first-child::after {
    transform: rotate(90deg);
  }

  td .name {
    font-weight: 600;
  }
  &:hover {
    td {
      background: #f1f2f3;
      cursor: pointer;
    }
  }
}
tr:not(.parent) {
  td {
    padding: 5px 8px;
  }
}
tr.level-1 {
  td:first-child {
    padding-left: 36px;
  }
}
tr:last-child {
  border-bottom: 1px solid #DBDBDB;
}
</style>
