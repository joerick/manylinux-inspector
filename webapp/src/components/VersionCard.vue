<script setup lang="ts">
import type Version from '@/model/Version';
import { dateFromImageTag, timeAgo } from '@/model/util';
import { computed } from 'vue';

const props = defineProps<{
  version: Version,
  isLatest?: boolean,
}>()
const date = computed(() => {
  const date = timeAgo(dateFromImageTag(props.version.tag))
  const firstLetter = date[0]
  return firstLetter.toUpperCase() + date.slice(1)
})
</script>

<template>
  <div class="version-card">
    <router-link :to="{ name: 'version', params: { name: version.name, tag: version.tag } }">
      <div class="tag">{{ version.tag }}</div>
    </router-link>
    <div class="date">{{ date }}</div>
    <div class="latest" v-if="isLatest">latest</div>
    <div class="spacer" style="height: 10px"></div>
    <div class="archs">Available for {{ version.archs.join(', ') }}</div>
  </div>
</template>

<style lang="scss" scoped>
.version-card {
  background-color: #fff;
  font-size: 14px;
  border-radius: 6px;
  box-shadow: 0 0.5em 1em -0.125em rgba(10,10,10,.1), 0 0 0 1px rgba(10,10,10,.02);
  color: #4a4a4a;
  padding: 13px 17px;
  position: relative;
  width: 100%;
  max-width: 410px;
}
.latest {
  position: absolute;
  top: 2px;
  right: 6px;
}
</style>
