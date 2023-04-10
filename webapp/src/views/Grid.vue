<script setup lang="ts">
import {get, getManylinuxVersions} from '@/model/model/model.js'
import Header from '@/components/Header.vue';
import { computed, ref } from 'vue';
import sortBy from 'lodash/sortBy'
import FixedHorizontalStickyVertical from '@/components/FixedHorizontalStickyVertical.vue';

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

const visibleRows = computed(() => {
  return sortedRows.value.filter(row => {
    if (row.keypath === 'pythons' || row.keypath === 'log') {
      return false
    }
    return true
  })
})

const rowsWithChildren = computed(() => {
  return new Set(rows.value.filter(row => row.parentId !== null).map(row => row.parentId!))
})

function displayName(row: Row): string {
  let match
  if (match = row.keypath.match(/^pythons\.cp(\d)(\d+)-[^\.]*$/)) {
    const major = match[1]
    const minor = match[2]
    const version = `${major}.${minor}`
    if (major == '2' && minor == '7') {
      // get the letters at the end of the id
      const variant = row.keypath.match(/[a-z]+$/)![0]
      return `Python ${version}<span class="variant">${variant}</span>`
    }
    return `CPython ${version}`
  } else if (match = row.keypath.match(/^pythons\.pp(\d)(\d+)-[^\.]*$/)) {
    const major = match[1]
    const minor = match[2]
    const version = `${major}.${minor}`
    return `PyPy ${version}`
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
function rowClicked(event: MouseEvent, row: Row) {
  if (!rowsWithChildren.value.has(row.keypath)) {
    return
  }
  event.preventDefault()
  event.stopPropagation()

  if (expandedRowIds.value.has(row.keypath)) {
    expandedRowIds.value.delete(row.keypath)
  } else {
    expandedRowIds.value.add(row.keypath)
  }
}

</script>

<template>
  <Header page="grid" />
  <div class="grid">
    <fixed-horizontal-sticky-vertical :height="35" :z-index="10" :sticky-top="0">
      <div class="search-bar">
        <img class="icon" src="@/assets/search-menu-icon.svg" alt="search-menu" role="button" />
        <input type="text" placeholder="all" v-model="searchTerm" />
      </div>
    </fixed-horizontal-sticky-vertical>
    <table cellspacing="0">
      <thead>
        <tr>
          <th></th>
          <th v-for="version in versions" :key="version.id">
            {{ version.name }}:<br>{{ version.tag }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in visibleRows"
            :key="row.keypath"
            :class="{parent: rowsWithChildren.has(row.keypath),
                     expanded: expandedRowIds.has(row.keypath),
                     hidden: row.parentId && !expandedRowIds.has(row.parentId)}"
            @click="rowClicked($event, row)">
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
.search-bar {
  background-color: black;
  padding: 0 36px;

  display: flex;
  gap: 10px;
  height: 35px;

  .icon {
    width: 21px;
    height: auto;
  }
  input[type="text"] {
    flex: 1;

    border: none;
    background: none;
    line-height: 35px;

    color: white;
    font-size: 14px;
    text-align: left;
    padding: 0;
    outline: none;
  }
}
table {
  padding: 0;
  text-align: left;
}
tbody {
  vertical-align: top;
}
th, td {
  margin: 0;
  padding: 2px;
  background: white;
  max-width: 230px;
}
th {
  white-space: nowrap;
  font-weight: 500;
  position: sticky;
  top: 35px;
  z-index: 1;
  background: white;
  border-bottom: 2px solid #DBDBDB;
  // box-shadow: 0 2px 2px -1px rgba(0, 0, 0, 0.4);

  font-weight: 600;
  padding: 9px 8px;
}
td:first-child, th:first-child {
  position: sticky;
  left: 0;
  z-index: 1;
  background: white;
  white-space: nowrap;
}
th:first-child {
  z-index: 2;
}
tr.hidden {
  visibility: collapse;
}

:global(body.is-safari .grid table tr.hidden) {
  display: none;
}
tr.parent {
  td {
    border-top: 1px solid #DBDBDB;
  }
  position: relative;

  td {
    padding: 16px 8px;
  }

  td:first-child {
    padding-left: 27px;
    :deep(.variant) {
      font-size: 9px;
      font-weight: bold;
      font-style: italic;
    }
  }

  td:first-child::after {
    content: '';
    display: inline-block;
    width: 13px;
    height: 13px;
    background-image: url(@/assets/disclosure-triangle.svg);
    background-position: center;
    background-repeat: no-repeat;
    position: absolute;
    left: 9px;
    top: 18px;
  }
  &.expanded td:first-child::after {
    transform: rotate(90deg);
  }

  td .name {
    font-weight: 600;
  }
  &:hover {
    td {
      background: #f1f2f3;
      cursor: pointer;
    }
  }
}
tr:not(.parent) {
  td {
    padding: 5px 8px;
  }
  td:first-child {
    padding-left: 36px;
  }
}
tr:last-child {
  border-bottom: 1px solid #DBDBDB;
}
</style>
