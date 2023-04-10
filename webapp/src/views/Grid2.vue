<script setup lang="ts">
import Version from '@/model/Version';
import { VersionsIndex, type VersionRef } from '@/model/VersionsIndex';
import { computedAsync, useAsyncState } from '@vueuse/core';
import { computed, reactive, ref, toRaw, watch } from 'vue';


const indexLoader = useAsyncState(
  VersionsIndex.get(),
  null,
)
const index = indexLoader.state

const searchTerm = ref('latest')

const versionRefs = computed(() => {
  const index = indexLoader.state.value
  if (!index) {
    return []
  }
  return index.search(searchTerm.value)
})

interface VersionCacheItem {
  ref: VersionRef,
  version: Version|null,
  abortController: AbortController,
}
const versionCache = reactive<{[filename: string]: VersionCacheItem|undefined}>({})

const versions = ref<VersionCacheItem[]>([])
watch(versionRefs, versionRefs => {
  const newVersions: VersionCacheItem[] = []
  for (const versionRef of versionRefs) {
    let versionCacheItem = versionCache[versionRef.filename]
    if (!versionCacheItem) {
      versionCacheItem = {
        ref: versionRef,
        version: null,
        abortController: new AbortController(),
      }

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
  versions.value = newVersions
})

watch(versions, (newState, oldState) => {
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

const fields = computed(() => {
  const result = new Array<{id: string, label: string}>()
  for (const versionCacheItem of versions.value) {
    if (versionCacheItem.version) {
      for (const field of versionCacheItem.version.fields) {
        if (!result.some(el => el.id === field.id)) {
          result.push({id: field.id, label: field.label})
        }
      }
    }
  }
  return result
})

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
          <th v-for="version in versions" :key="version.ref.filename">
            {{ version.ref.name }}:<br>{{ version.ref.tag }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="field in fields">
          <td>
            <span class="name" v-html="field.label"></span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style lang="scss" scoped>
</style>
