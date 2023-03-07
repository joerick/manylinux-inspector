<script setup lang="ts">
import reports from '@/data/reports.json';
import {get} from '@/model'

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

function getRow(field: string) {
  const result = [field]
  for (const image of reports) {
    result.push(get(image.data, field))
  }
  return result
}

const headings = ['', ...reports.map(item => item.metadata.image)]
const rows = fields.map(getRow)
</script>

<template>
  <div class="home">
    <table>
      <thead>
        <tr>
          <th v-for="heading in headings" :key="heading">
            {{ heading }}
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
}
</style>
