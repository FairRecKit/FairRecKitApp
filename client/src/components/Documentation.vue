<script setup>
/* This program has been developed by students from the bachelor Computer Science at
Utrecht University within the Software Poject course.
© Copyright Utrecht University (Department of Information and Computing Sciences) */
/*
Documentation tab which shows all algorithms, metrics, datasets, etc. and their description.
*/

import { ref } from 'vue'
// import { structure } from '../documentation/documentation_structure.vue'
import {
  tree,
  flatTree,
  openParents,
  formatId,
} from '../documentation/documentation_tree2'
import TreeMenu from '../documentation/TreeMenu.vue'
// import { doctext } from '../documentation/documentation_items.vue'

// const collapse = ref([])
// let itemDicts = ref()
let sidenavOpened = ref()
// let structure1D = ref()

// itemDicts = parse(doctext)
sidenavOpened = false
// structure1D = parseStructure(structure)

/**
 * Parses the content of documentation_items.txt into items.
 * @param {String} text - documentation_items.txt as one string.
 * @return {[Dict]} Array of items represented as a dictionary.
 */
function parse(text) {
  const stringItems = parseTextIntoItems(text)
  const items = {}
  for (let i = 0; i < stringItems.length; i++) {
    const idict = parseItem(stringItems[i])
    items[idict.name] = idict
  }
  return items
}

/**
 * Parses documents_items.txt into an array of items.
 * @param {String} text - The whole content of documents_items.txt as one String.
 * @return {[String]} An array of strings of items: ["<name>...</name>\n<description>...</description>", "..."].
 */
function parseTextIntoItems(text) {
  // An item is defined as anything between -{...}- as defined in documents_items.txt
  const items = []
  let item = ''
  let readItem = false
  const textLines = text.split('\n')

  for (let j = 0; j < textLines.length; j++) {
    // Parse each sentence
    const line = textLines[j]
    for (let i = 0; i < line.length; i++) {
      const character = line[i]
      if (character + line[i + 1] == '-{') {
        readItem = true
        i += 1
        continue
      }
      if (character + line[i + 1] == '}-') {
        readItem = false
        items.push(item)
        item = ''
      }
      if (readItem) {
        item += character
      }
    }
    item += '\n'
  }
  return items
}

/**
 * Parses an item into a dictionary so that it can be referred to as e.g., dict["name"], dict["description"].
 * @param {String} item - An item as a string: "<name>...</name>\n<description>...</description>".
 * @return {Dict} Dictionary of an item as key, value: dict["name"] = "Algorithm 123".
 */
function parseItem(item) {
  const dict = {}
  let key = ''
  let value = ''
  let keytagFound = false // Prevents nested tags.
  const itemLines = item.split('\n')
  for (let j = 0; j < itemLines.length; j++) {
    const words = itemLines[j].split(' ')
    for (let i = 0; i < words.length; i++) {
      const word = words[i]
      if (word.match(/<.*>/)) {
        const endTag = new RegExp('</' + key + '>', 'g') // Ending tag e.g., </name>.
        if (word.match(endTag)) {
          value = value.slice(0, -1) // Remove trailing whitespace.
          dict[key] = value
          key = ''
          value = ''
          keytagFound = false
          i -= 1
        }
        // Starting tag e.g., <name>.
        else if (!keytagFound && word.match(/<[^\/].*>/)) {
          keytagFound = true
          key = word.match(/(?<=<).*(?=>)/)[0]
          value = ''
          continue
        }
      }
      if (key) {
        value += word + ' '
      }
    }
    value += '\n'
  }
  return dict
}

/**
 * Parses documentation_structure.vue into a 1D array of {String, Int}.
 * @param {[String]} struct Mulitdimensional array of different lengths.
 * @return {[{String, Int}]} 1-dimensional array of headers.
 */
function parseStructure(struct) {
  const res = []
  parsePartialStructure(struct, -1)

  /**
   * Recursive function to flatten a jagged array.
   * @param {[String]} struct
   * @param {Int} startDepth
   */
  function parsePartialStructure(struct, startDepth) {
    for (let j = 0; j < struct.length; j++) {
      const item = struct[j]
      if (item instanceof Array) {
        // List of subheaders
        parsePartialStructure(item, startDepth + 1)
      } else {
        // Regular header
        res.push({ name: item, depth: startDepth })
      }
    }
  }
  return res
}

/**
 * Navigation sidebar toggle collapse
 */
function openCloseNav() {
  if (sidenavOpened.value) {
    closeNav()
  } else {
    openNav()
  }
}
function openNav() {
  sidenavOpened = true
  document.getElementById('docSidenav').style.width = '250px'
  document.getElementById('main').style.marginLeft = '250px'
}
function closeNav() {
  sidenavOpened = false
  document.getElementById('docSidenav').style.width = '0'
  document.getElementById('main').style.marginLeft = '0'
}
</script>

<style>
/* Can be added in custom.scss */
table {
  font-family: arial, sans-serif;
  border-collapse: collapse;
  width: 100%;
}

td,
th {
  border: 1px solid #dddddd;
  text-align: left;
  padding: 8px;
}

tr:nth-child(even) {
  background-color: #dddddd;
}

.sidenav {
  height: 100%;
  width: 0;
  position: fixed;
  z-index: 1;
  top: 0;
  left: 0;
  background-color: #111;
  overflow-x: hidden;
  transition: 0.5s;
  padding-top: 60px;
}

.sidenav a {
  padding: 2px 2px 8px 15px;
  text-decoration: none;
  font-size: 15px;
  color: #818181;
  display: block;
  transition: 0.3s;
}

.sidenav a:hover {
  color: #017c8e;
}

.sidenav .closebtn {
  position: absolute;
  top: 0;
  right: 25px;
  font-size: 36px;
  margin-left: 50px;
}

#main {
  transition: margin-left 0.5s;
  padding: 16px;
}

@media screen and (max-height: 450px) {
  .sidenav {
    padding-top: 15px;
  }
  .sidenav a {
    font-size: 18px;
  }
}

pre {
  background-color: #eee;
  border: 1px solid #999;
  display: block;
  padding: 5px;
  margin: 5px;
}

/*
pre {
  counter-reset: line;
}
code {
  counter-increment: line;
}
code:before {
  content: counter(line);
  margin-right: 30px;
  -webkit-user-select: none;
  color: gray;
}
*/
</style>

<template>
  <div id="main" class="ps-0">
    <!-- Open-close button -->
    <span
      class="position-fixed bg-dark text-white px-2 rounded-end"
      style="font-size: 30px; cursor: pointer"
      v-on:click="openCloseNav()"
      >&#9776;</span
    >
    <!-- Navigation sidebar -->
    <div id="docSidenav" class="sidenav bg-secondary">
      <!--<a href="javascript:void(0)" class="closebtn float-end m-0" v-on:click="closeNav()">&times;</a>-->
      <b-link
        class="position-relative py-0"
        data-toggle="collapse"
        :href="'#' + formatId(item.name)"
        v-on:click="openParents(item)"
        v-for="item in flatTree"
        :key="item"
      >
        <!-- Indentation to indicate items and subitems -->
        <span style="-webkit-user-select: none">{{
          '&nbsp;&nbsp;&nbsp;'.repeat(item.depth)
        }}</span
        >{{ item.name }}
      </b-link>
    </div>

    <!-- B-card items -->
    <div
      id="app"
      class="text-right pb-2 mx-5"
      v-for="item in tree.nodes"
      :key="item"
    >
      <TreeMenu :label="item.label" :nodes="item.nodes"></TreeMenu>
    </div>
  </div>
</template>
