<script setup lang="ts">
import { computed, reactive, ref, type StyleValue } from 'vue';
import { useElementBounding } from '@vueuse/core';
import FixedHorizontal from './FixedHorizontal.vue';

const props = defineProps<{
  page?: 'standards' | 'grid',
  belowHeight?: number,
}>()

</script>

<template>
  <header>
    <fixed-horizontal :height="60">
      <div class="main">
        <div class="left">
          <img class="logo" src="@/assets/icon.svg" alt="Icon" />
          <div class="site-name">
            Manylinux Inspector
          </div>
          <slot name="left" />
        </div>
        <div class="nav-items">
          <div class="nav-item" :class="{active: page === 'standards'}">
            <img src="@/assets/version-icon.svg" alt="Version icon" class="icon">
            <span class="name">Standards</span>
          </div>
          <div class="nav-item" :class="{active: page === 'grid'}">
            <img src="@/assets/grid-icon.svg" alt="grid icon" class="icon">
            <span class="name">Grid</span>
          </div>
        </div>
      </div>
    </fixed-horizontal>
  </header>
</template>

<style lang="scss" scoped>
header {
  color: white;
  font-size: 16px;
}

.main {
  background-color: #1f2933;
  height: 60px;

  display: flex;
  align-items: center;
  height: 60px;
  gap: 14px;
  padding: 0 36px;
}

.logo {
  height: 30px;
}

.site-name {
  font-weight: 600;
  font-size: 18px;
  flex: 1;
}
.left, .nav-items {
  display: flex;
  align-items: center;
  height: 100%;
}
.left {
  gap: 14px;
}
.nav-items {
  justify-content: flex-end;
  flex: 1;
}
.nav-item {
  height: 100%;

  display: flex;
  align-items: center;
  gap: 7px;
  padding: 0 20px;
  &.active {
    background-color: black;
  }
}

</style>
