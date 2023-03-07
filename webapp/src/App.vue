<script setup lang="ts">

</script>

<template>
  <header>
    <div class="margins">
      <img class="logo" src="@/assets/icon.svg" alt="Icon" />
      <div class="name">
        Manylinux Inspector
      </div>
    </div>
  </header>
  <main>
    <router-view />
  </main>
</template>

<style scoped>
header {
  border-bottom: 3px solid currentColor;
}

header .margins {
  display: flex;
  align-items: center;
  height: 50px;
  gap: 10px;
}

.logo {
  height: 30px;
}

.name {
  font-weight: 700;
  flex: 1;
}

</style>
