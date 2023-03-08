<script setup lang="ts">
import reports from '@/data/reports.json';
import {get, getManylinuxVersions} from '@/model'
import Header from '@/components/Header.vue';
import { computed, ref } from 'vue';


const allVersions = getManylinuxVersions()
const searchTerm = ref('')
const versions = computed(() => {
  return allVersions.filter(item => (
    item.name.toLowerCase().includes(searchTerm.value.toLowerCase())
    || item.tag.toLowerCase().includes(searchTerm.value.toLowerCase())
  ))
})

function listKeypaths(object: any): string[] {
  const keypaths = [];
  for (const key in object) {
    if (object.hasOwnProperty(key)) {
      if (typeof object[key] === 'object') {
        const subkeypaths = listKeypaths(object[key]);
        for (const subkeypath of subkeypaths) {
          keypaths.push(key + '.' + subkeypath);
        }
      } else {
        keypaths.push(key);
      }
    }
  }
  return keypaths;
}

function extractFields(): string[] {
  const headers = new Set<string>()
  for (const item of reports) {
    const keypaths = listKeypaths(item.data)
    for (const keypath of keypaths) {
      headers.add(keypath)
    }
  }
  const result = Array.from(headers)
  result.sort()
  return result
}

const fields = [
  ...extractFields(),
]

const rows = computed(() => {
  const result = []

  for (const field of fields) {
      const row = [field, ...versions.value.map(version => version.getField(field))]
      result.push(row)
  }

  return result
})

const headings = computed(() => {
  return ['', ...versions.value.map(item => `${item.name}:<br>${item.tag}`)]
})

</script>

<template>
  <Header>
    <template #right>
      <input type="text" placeholder="Search images" v-model="searchTerm" />
    </template>
  </Header>
  <div class="home">
    <table>
      <thead>
        <tr>
          <th v-for="heading in headings" :key="heading" v-html="heading">
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows" :key="row[0]">
          <td v-for="cell in row" :key="cell">
            {{ cell }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style lang="scss" scoped>
table, th, td {
  margin: 0;
  padding: 2px;
  border: 1px solid #999;
  // border-collapse: collapse;
}
th {
  white-space: nowrap;
  font-weight: 500;
}

</style>
