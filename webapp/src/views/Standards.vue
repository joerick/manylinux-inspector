<script setup lang="ts">
import Header from '@/components/Header.vue';
import { VersionsIndex, type VersionRef } from '@/model/VersionsIndex';
import { compareStandardNames, standards } from '@/model/standards';
import { useAsyncState } from '@vueuse/core';
import { computed } from 'vue';
import VersionCard from '@/components/VersionCard.vue';
import { groupBy, uniqBy } from 'lodash-es';

const indexLoader = useAsyncState(
  VersionsIndex.get(),
  null,
)

const availableStandards = computed(() => {
  const index = indexLoader.state.value;
  if (!index) return standards

  let result = index.allVersionRefs.map(ref => ({
    name: ref.name,
    description: getStandardDescription(ref.name),
  })) ?? []

  result = uniqBy(result, 'name')
  result.sort((a, b) => compareStandardNames(a.name, b.name))
  return result
})

const latestVersions = computed(() => {
  const index = indexLoader.state.value;
  if (!index) return {}

  const refs = index.latestVersionRefs.slice()
  refs.sort((a, b) => {
    return b.tag.localeCompare(a.tag)
  })

  return groupBy(refs, ref => ref.name)
}, {})

function getStandardDescription(name: string) {
  return standards.find(s => s.name == name)?.description ?? null
}
</script>

<template>
  <div class="standards">
    <Header page="standards" />

    <div class="spacer" style="height: 60px;"></div>

    <div class="margins">
      <div class="standard" v-for="standard in availableStandards">
        <h2>
          <router-link :to="{ name: 'standard', params: { name: standard.name } }" >
            {{ standard.name }}
          </router-link>
        </h2>
        <p>{{ standard.description }}</p>
        <div class="spacer" style="height: 5px"></div>
        <div class="cards">
          <VersionCard v-for="version in latestVersions[standard.name]"
                       :version="version"
                       :latest-info="indexLoader.state.value?.latestInfo(version)" />
        </div>
        <div class="spacer" style="height: 10px"></div>
        <RouterLink :to="{ name: 'standard', params: { name: standard.name } }" >
          {{ latestVersions[standard.name] ? "Other versions >" : "Browse versions >" }}
        </RouterLink>
      </div>
    </div>

    <div class="spacer" style="height: 60px;"></div>
  </div>
</template>

<style lang="scss" scoped>
.standard {
  margin-bottom: 25px;
  h2 a {
    color: inherit;
    text-decoration: none;
  }
}
.cards {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
</style>
