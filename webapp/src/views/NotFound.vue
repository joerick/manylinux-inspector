<script setup lang="ts">
import Header from '@/components/Header.vue';
</script>

<template>
  <div class="not-found">
    <Header />

    <div class="spacer" style="height: 60px;"></div>

    <div class="margins">
      <h2>
        404 Not found
      </h2>
      <RouterLink to="/">Go to the home page</RouterLink>
    </div>

  </div>
</template>

<style lang="scss" scoped>
</style>
