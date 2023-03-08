<template>
  <header>
    <div class="left">
      <img class="logo" src="@/assets/icon.svg" alt="Icon" />
      <div class="name">
        Manylinux Inspector
      </div>
      <slot name="left" />
    </div>
    <div class="right">
      <slot name="right" />
    </div>
  </header>
</template>

<style lang="scss" scoped>
header {
  border-bottom: 3px solid currentColor;
  display: flex;
  align-items: center;
  height: 50px;
  gap: 10px;
  padding: 0 20px;
}

.logo {
  height: 30px;
}

.name {
  font-weight: 700;
  flex: 1;
}

.left, .right {
  display: flex;
  gap: 10px;
  align-items: center;
}
.right {
  justify-content: flex-end;
  flex: 1;
}

</style>
