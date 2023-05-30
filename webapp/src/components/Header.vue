<script setup lang="ts">
import { ref } from 'vue';
import FixedHorizontal from './FixedHorizontal.vue';

const props = defineProps<{
  page?: 'standards' | 'grid',
  belowHeight?: number,
}>()

const menuOpen = ref(false)

</script>

<template>
  <header>
    <fixed-horizontal :height="60" :z-index="20">
      <div class="main">
        <div class="left">
          <router-link :to="{name: 'grid'}" class="site-link">
            <img class="logo" src="@/assets/icon.svg" alt="Icon" />
            <div class="site-name">
              Manylinux Inspector
            </div>
          </router-link>
          <a class="about-link" href="https://github.com/joerick/manylinux-inspector#readme">About</a>
        </div>
        <div class="mobile-expand-button" @click="menuOpen = !menuOpen">
          <div class="l"></div>
          <div class="l"></div>
          <div class="l"></div>
        </div>
        <div class="nav-items" :class="{'menu-open': menuOpen}">
          <router-link :to="{name: 'standards'}" class="nav-item" :class="{active: page === 'standards'}">
            <img src="@/assets/version-icon.svg" alt="Version icon" class="icon">
            <span class="name">Standards</span>
          </router-link>
          <router-link :to="{name: 'grid'}" class="nav-item" :class="{active: page === 'grid'}">
            <img src="@/assets/grid-icon.svg" alt="grid icon" class="icon">
            <span class="name">Grid</span>
          </router-link>
        </div>
      </div>
    </fixed-horizontal>
  </header>
</template>

<style lang="scss" scoped>
header {
  color: white;
  font-size: 16px;

  a {
    text-decoration: none;
    &:link, &:visited {
      color: inherit;
    }
  }
}

.main {
  background-color: #1f2933;
  min-height: 60px;

  display: flex;
  align-items: flex-start;
  gap: 0 14px;
  padding: 0 36px;

  @media (max-width: 599px) {
    flex-direction: column;
    align-items: stretch;
  }
}

.logo {
  height: 30px;
}

.site-name {
  font-weight: 600;
  font-size: 18px;
  flex: 1;
}
.about-link {
  font-size: 13px;
  opacity: 0.4;
  color: white;
  font-weight: 400;
  margin-left: 15px;

  position: relative;
  top: 2px;

  @media (max-width: 599px) {
    display: none;
  }
}
.left, .nav-items, .site-link {
  display: flex;
  align-items: center;
  height: 100%;
}
.left {
  height: 60px;
  align-items: center;
}
.site-link {
  gap: 14px;
}
.nav-items {
  justify-content: flex-end;
  flex: 1;
  .nav-item {
    line-height: 60px;

    display: flex;
    align-items: center;
    gap: 7px;
    padding: 0 20px;

    &.active {
      background-color: black;
    }
  }

  @media (max-width: 599px) {
    flex-direction: column;
    align-items: flex-end;
    &:not(.menu-open) {
      .nav-item {
        display: none;
      }
    }
  }
}
.mobile-expand-button {
  position: absolute;
  top: 0;
  right: 36px;
  height: 60px;
  width: 60px;

  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;

  cursor: pointer;

  gap: 4px 0;

  @media (min-width: 600px) {
    display: none;
  }
  .l {
    width: 20px;
    height: 2px;
    background-color: white;
  }
}
</style>
