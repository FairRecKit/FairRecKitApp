<script setup>
/* This program has been developed by students from the bachelor Computer Science at
Utrecht University within the Software Project course.
© Copyright Utrecht University (Department of Information and Computing Sciences) */

import { onMounted, ref } from 'vue'
import MusicModal from './ItemDetail/MusicModal.vue'
import { getSpotifyInfo } from '../helpers/songInfo'
const track = ref()
const tracks = ref([])
const query = ref({ track: 'orion', artist: 'metallica' })

const modalShow = ref(false)

onMounted(async () => {
  getSpotifyTrack()
})

/**
 * Get Spotify track info from track and artist query

 */
async function getSpotifyTrack() {
  tracks.value = await getSpotifyInfo(query.value.track, query.value.artist)

  track.value = tracks.value.items[0]
}
</script>

<template>
  <b-container>
    <h1 class="text-center">Music Detail</h1>
    <b-row>
      <b-form @submit="getSpotifyTrack">
        <b-row>
          <b-col>
            <b-form-group label="Track">
              <b-form-input
                v-model="query.track"
                placeholder="Enter track name"
              />
            </b-form-group>
          </b-col>
          <b-col>
            <b-form-group label="Artist">
              <b-form-input
                v-model="query.artist"
                placeholder="Enter artist name"
              />
            </b-form-group>
          </b-col>
          <b-col>
            <b-button type="submit" variant="primary">Submit</b-button>
          </b-col>
        </b-row>
      </b-form>
    </b-row>
    <b-card>
      <h3>Found tracks:</h3>
      <ul>
        <li v-for="queryTrack in tracks.items" :key="queryTrack">
          {{ queryTrack.name }}
        </li>
      </ul>
    </b-card>

    <template v-if="track">
      <b-button
        style="width: 20vw; display: block"
        class="mx-auto"
        variant="primary"
        @click="modalShow = !modalShow"
        >Show track
      </b-button>
      <MusicModal v-model="modalShow" :track="track" />
    </template>
  </b-container>
</template>
