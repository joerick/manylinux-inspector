<script setup lang="ts">
import {get, getManylinuxVersions} from '@/model'
import Header from '@/components/Header.vue';
import { computed, ref } from 'vue';
import {sortBy} from 'lodash'

const allVersions = getManylinuxVersions()
const searchTerm = ref('')
const versions = computed(() => {
  return allVersions.filter(version => {
    const versionStr = `${version.name}:${version.tag}`
    return versionStr.toLowerCase().includes(searchTerm.value.toLowerCase())
  })
})

const expandedRowIds = ref(new Set<string>(['pythons']))

interface Row {
  keypath: string,
  name: string,
  parentId: string|null,
  values: {
    [versionId: string]: string,
  }
}

const rows = computed<Row[]>(() => {
  const result: Row[] = []

  function rowWithKeypath(keypath: string): Row {
    const existing = result.find(row => row.keypath === keypath)
    if (existing) {
      return existing
    }

    const keypathParts = keypath.split('.')
    const parentKeypath = keypathParts.slice(0, -1).join('.') || null
    const parentRow = parentKeypath ? rowWithKeypath(parentKeypath) : null
    const key = keypathParts.slice().pop()!

    const row = {
      keypath,
      name: key,
      parentId: parentRow?.keypath ?? null,
      values: {},
    }
    result.push(row)

    return row
  }

  for (const version of versions.value) {
    const keypaths = version.getKeypaths()
    for (const keypath of keypaths) {
      const row = rowWithKeypath(keypath)
      row.values[version.id] = version.getField(keypath)
    }
  }

  return result
})

const sortedRows = computed(() => {
  const regex = /pythons\.(\w*?)(\d)(\d+)-(.*)/
  /* let answer = wordsArr.sort((a,b) => {
    return a.match(regex) - b.match(regex);
  });*/
  const annotatedWords = rows.value.map(row => {
    const keypath = row.keypath
  	const match = keypath.match(regex)
    if (!match) return {row, keypath}
    return {
      row,
      keypath,
     	interpreter: match[1],
      major: parseInt(match[2]),
      minor: parseInt(match[3]),
      rest: match[4],
    }
  })

  return sortBy(annotatedWords, ['interpreter', 'major', 'minor', 'rest', 'keypath']).map(item => item.row)
})


// function extractFields(): string[] {
//   const headers = new Set<string>()
//   for (const item of reports) {
//     const keypaths = listKeypaths(item.data)
//     for (const keypath of keypaths) {
//       headers.add(keypath)
//     }
//   }
//   const result = Array.from(headers)
//   result.sort()
//   return result
// }

// const fields = [
//   ...extractFields(),
// ]

// const rows = computed(() => {
//   const result = []

//   for (const field of fields) {
//       const row = [field, ...versions.value.map(version => version.getField(field))]
//       result.push(row)
//   }

//   return result
// })

// const headings = computed(() => {
//   return ['', ...versions.value.map(item => `${item.name}:<br>${item.tag}`)]
// })

const visibleRows = computed(() => {
  return sortedRows.value.filter(row => {
    if (row.keypath === 'pythons') {
      return false
    }
    if (row.parentId === null) {
      return true
    }
    return expandedRowIds.value.has(row.parentId)
  })
})

const rowsWithChildren = computed(() => {
  return new Set(rows.value.filter(row => row.parentId !== null).map(row => row.parentId!))
})
function displayName(row: Row): string {
  let match
  if (match = row.keypath.match(/pythons\.cp(\d)(\d+)-.*/)) {
    const major = match[1]
    const minor = match[2]
    const version = `${major}.${minor}`
    return `CPython ${version}<br>${row.name}`
  } else if (match = row.keypath.match(/pythons\.pp(\d)(\d+)-.*/)) {
    const major = match[1]
    const minor = match[2]
    const version = `${major}.${minor}`
    return `PyPy ${version}<br>${row.name}`
  }
  return row.name
}

function values(row: Row): {[versionId: string]: string} {
  if (rowsWithChildren.value.has(row.keypath)) {
    // This is a parent row
    if (row.keypath.match(/pythons\.[\w-]+/)) {
      // This is a python row
      // return the value of the 'python' field
      const pythonKeypath = `${row.keypath}.python`
      const pythonRow = rows.value.find(row => row.keypath === pythonKeypath)
      if (pythonRow) {
        return pythonRow.values
      }
    }
  }
  return row.values
}


</script>

<template>
  <Header>
    <template #right>
      <input type="text" placeholder="Search images" v-model="searchTerm" />
    </template>
  </Header>
  <div class="home">
    <table  cellspacing="0">
      <thead>
        <tr>
          <th></th>
          <th v-for="version in versions" :key="version.id">
            {{ version.name }}:<br>{{ version.tag }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in visibleRows" :key="row.keypath">
          <td>
            <span class="name" v-html="displayName(row)"></span>
          </td>
          <td v-for="version in versions" :key="version.id">
            {{ values(row)[version.id] }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style lang="scss" scoped>
table {
  position: relative;
  // border-collapse: collapse;
}
table, th, td {
  margin: 0;
  padding: 2px;
  border: 1px solid #999;
  background: white;
}
th {
  white-space: nowrap;
  font-weight: 500;
  position: sticky;
  top: 0;
  background: white;
  box-shadow: 0 2px 2px -1px rgba(0, 0, 0, 0.4);
}
td:first-child, th:first-child {
  position: sticky;
  left: 0;
  background: white;
  white-space: nowrap;
}
th:first-child {
  z-index: 1;
}

</style>
