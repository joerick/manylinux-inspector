<script setup lang="ts">
import { VersionsIndex, type VersionRef } from '@/model/VersionsIndex';
import { standards } from '@/model/standards';
import { useAsyncState } from '@vueuse/core';
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import NotFound from './NotFound.vue';
import VersionCard from '@/components/VersionCard.vue';
import Header from '@/components/Header.vue';

const route = useRoute()
const standardName = computed(() => route.params.name as string)

const standard = computed(() => {
  return standards.find(s => s.name == standardName.value)
})

const indexLoader = useAsyncState(
  VersionsIndex.get(),
  null,
)

interface VersionRefWithLatest extends VersionRef {
  isLatest?: boolean
}
const standardVersionsLoader = useAsyncState(
  async () => {
    const index = await VersionsIndex.get()
    const refs = index.allVersionRefs.filter(ref => ref.name == standardName.value) as VersionRefWithLatest[]

    if (refs.length == 0) throw new Error('Versions not found')

    for (const ref of refs) {
      ref.isLatest = index.latestVersionRefs.some(latestRef =>
        ref.filename == latestRef.filename
      )
    }

    refs.sort((a, b) => {
      return b.tag.localeCompare(a.tag)
    })

    return refs
  },
  null,
)

const versions = standardVersionsLoader.state

</script>

<template>
  <NotFound v-if="!standard" />
  <div v-else class="standard">
    <Header page="standards" />

    <div class="spacer" style="height: 60px;"></div>

    <div class="margins">
      <h2>
        {{ standard.name }}
      </h2>
      <p>{{ standard.description }}</p>
      <div class="spacer" style="height: 5px"></div>

      <div class="loading" v-if="standardVersionsLoader.isLoading.value">Loading…</div>
      <div class="error" v-if="standardVersionsLoader.error.value">{{ standardVersionsLoader.error.value }}</div>
      <div class="cards" v-if="versions">
        <VersionCard v-for="version in versions"
                     :version="version"
                     :latest-info="indexLoader.state.value?.latestInfo(version)" />
      </div>
      <div class="spacer" style="height: 10px"></div>
      <RouterLink :to="{ name: 'grid', query: { q: standard.name } }" >
        View in grid >
      </RouterLink>
    </div>

    <div class="spacer" style="height: 60px;"></div>
  </div>
</template>

<style lang="scss" scoped>
.cards {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
</style>
