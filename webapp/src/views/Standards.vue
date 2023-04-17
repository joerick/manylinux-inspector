<script setup lang="ts">
import Header from '@/components/Header.vue';
import Version from '@/model/Version';
import { VersionsIndex } from '@/model/VersionsIndex';
import { compareStandardNames, standards } from '@/model/standards';
import { useAsyncState } from '@vueuse/core';
import { computed } from 'vue';
import VersionCard from '@/components/VersionCard.vue';
import { groupBy, union, uniqBy } from 'lodash';
import { unique } from '@/model/util';

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

const latestImagesLoader = useAsyncState(async () => {
  const index = await VersionsIndex.get();

  const latestVersions = await Promise.all(
    index.latestVersionRefs.map(ref => Version.getWithFilename(ref.filename))
  )
  return groupBy(latestVersions, version => version.name)
}, {})
const latestImages = latestImagesLoader.state

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
          <router-link :to="{ name: 'grid', query: { q: standard.name } }" >
            {{ standard.name }}
          </router-link>
        </h2>
        <p>{{ standard.description }}</p>
        <div class="spacer" style="height: 5px"></div>
        <div class="cards">
          <VersionCard v-for="version in latestImages[standard.name]"
                       :version="version"
                       :is-latest="true" />
        </div>
        <div class="spacer" style="height: 10px"></div>
        <RouterLink :to="{ name: 'grid', query: { q: standard.name } }" >
          {{ latestImages[standard.name] ? "Other versions >" : "Browse versions >" }}
        </RouterLink>
      </div>
    </div>
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
