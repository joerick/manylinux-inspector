<script setup lang="ts">
/**
 * A component that fixes the horizontal position of its children, but they
 * still scroll vertically
 */

import { useElementBounding } from '@vueuse/core';
import { computed, ref, type StyleValue } from 'vue';

const props = defineProps<{
  height: number;
}>()

const placeholderElement = ref<HTMLElement>()
const placeholderRect = useElementBounding(placeholderElement)

const contentStyle = computed<StyleValue>(() => ({
  top: `${placeholderRect.y.value}px`,
  height: `${props.height}px`,
}))

const placeholderStyle = computed<StyleValue>(() => ({
  height: `${props.height}px`,
}))

</script>

<template>
  <div class="fixed-horizontal">
    <div class="content" ref="contentElement" :style="contentStyle">
      <slot />
    </div>
    <div class="placeholder" ref="placeholderElement" :style="placeholderStyle"></div>
  </div>
</template>

<style lang="scss" scoped>
.content {
  position: fixed;
  left: 0;
  right: 0;
}
</style>
