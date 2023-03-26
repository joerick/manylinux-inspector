<script setup lang="ts">
/**
 * A component that fixes the horizontal position of its children, but sticky
 * vertically
 */

import { useElementBounding } from '@vueuse/core';
import { computed, ref, type StyleValue } from 'vue';

const props = defineProps<{
  height: number;
  stickyTop: number;
  zIndex: number;
}>()

const placeholderElement = ref<HTMLElement>()
const placeholderRect = useElementBounding(placeholderElement)

const contentStyle = computed<StyleValue>(() => ({
  top: `${placeholderRect.y.value}px`,
  height: `${props.height}px`,
  zIndex: props.zIndex,
}))

const placeholderStyle = computed<StyleValue>(() => ({
  top: `${props.stickyTop}px`,
  height: `${props.height}px`,
}))

</script>

<template>
  <div class="fixed-horizontal-sticky-vertical">
    <div class="content" ref="contentElement" :style="contentStyle">
      <slot />
    </div>
    <div class="placeholder" ref="placeholderElement" :style="placeholderStyle"></div>
  </div>
</template>

<style lang="scss" scoped>
.fixed-horizontal-sticky-vertical {
  display: contents;
}
.content {
  position: fixed;
  left: 0;
  right: 0;
}
.placeholder {
  position: sticky;
  top: 0;
}
</style>
