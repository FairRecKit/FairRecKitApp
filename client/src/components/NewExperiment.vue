<script setup>
/* This program has been developed by students from the bachelor Computer Science at
Utrecht University within the Software Project course.
© Copyright Utrecht University (Department of Information and Computing Sciences) */
import { ref, watch } from 'vue'
import FormGroupList from './Form/FormGroupList.vue'
import { sendMockData } from '../test/mock/mockExperimentOptions.js'
import { store, switchToTab, tabs, getQueue } from '../store.js'
import { API_URL, DEV } from '../api'
import {
  emptyFormGroup,
  validateEmail,
  reformat,
} from '../helpers/optionsFormatter'
import Tags from './Tags.vue'
import { useFetch } from '../composables/useFetch'
import endToEndMock from '../test/mock/endToEndMock.json'

import filterForm from '../test/mock/filterMock.json'
// GET request: Get available options for selection from server
const { data, error, retry } = useFetch(API_URL + '/experiment/options')
const options = ref()
// Store the settings of the form in a reference
const form = ref(initForm())
const metadata = ref({})
const experimentMethods = [
  { text: 'Recommendation (default)', value: 'recommendation' },
  { text: 'Prediction', value: 'prediction' },
]

/**
 * Initialise settings when the options are first retrieved
 */
watch(
  () => data.value,
  (newData, oldData) => {
    options.value = newData.options
    if (newData && !oldData) {
      initSettings()
    }
  }
)

/**
 * Watch for change of global form settings, copy them
 */
watch(
  () => store.settings,
  (newSettings) => {
    console.log('newExperiment watch new settings:', newSettings)
    form.value = newSettings.form
    metadata.value = newSettings.metadata
    switchToTab(tabs.newExperiment)
  }
)

/**
 * Update the options based on the chosen datasets
 */
watch(
  () => reformat(form.value.lists.datasets),
  (newDatasets, oldDatasets) => {
    if (
      [...newDatasets.keys()].some(
        (i) =>
          !oldDatasets[i] ||
          newDatasets[i].name !== oldDatasets[i].name ||
          (newDatasets[i].matrix && !oldDatasets[i].matrix) ||
          (newDatasets[i].matrix &&
            oldDatasets[i].matrix &&
            newDatasets[i].matrix.name !== oldDatasets[i].matrix.name)
      )
    ) {
      /* console.log('dataset or matrix change')
      console.log(
        'new datasets',
        newDatasets[0].matrix,
        oldDatasets[0] && oldDatasets[0].matrix
      ) */
      setOptions(newDatasets)
    }
  },
  {
    immediate: false,
  }
)

// POST request: Get available options for selection from server
async function setOptions(chosenDatasets = []) {
  const requestOptions = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ datasets: chosenDatasets }),
  }
  const response = await fetch(API_URL + '/experiment/options', requestOptions)
  const data = await response.json()
  options.value = JSON.parse(JSON.stringify(data.options))
  // console.log('new options', options.value)
}

// POST request: Send form to server.
async function sendToServer() {
  const sendForm = JSON.parse(JSON.stringify(form.value)) // clone

  sendForm.rawSettings = JSON.parse(JSON.stringify(form.value)) // send raw settings for copying later TODO refactor
  // console.log('raw form settings', sendForm.rawSettings)
  sendForm.lists.approaches = reformat(sendForm.lists.approaches)
  sendForm.lists.metrics = reformat(sendForm.lists.metrics)
  sendForm.lists.datasets = reformat(sendForm.lists.datasets)
  console.log('sendForm', sendForm)

  const requestOptions = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      metadata: metadata.value,
      settings: sendForm,
    }),
  }
  await fetch(API_URL + '/experiment/', requestOptions)
  // Update queue
  getQueue()
}

// Declare default values of the form
function initSettings() {
  form.value = initForm()
  metadata.value = {}
}

// Initialise form group list settings
function initForm() {
  return {
    lists: {
      datasets: emptyFormGroup(true),
      metrics: emptyFormGroup(),
      approaches: emptyFormGroup(true),
    },
    recommendations: options.value && options.value.defaults.recCount.default, // The default amount of recommendations per user
    experimentMethod: 'recommendation', // The default experiment type
    includeRatedItems: true,
  }
}

/**
 * Avoid characters that cause path errors in the experiment name
 */
function validName(inputName) {
  if (inputName)
    return !['/', '\\\\', '.'].some((badString) =>
      inputName.includes(badString)
    )
}
</script>

<template>
  <!--TODO refactor to loading component-->
  <div v-if="error">
    <p>Oops! Error encountered: {{ error.message }}</p>
    <b-button @click="retry">Retry</b-button>
  </div>
  <!-- Show a loading screen unless data has been loaded -->
  <b-overlay v-else :show="!data">
    <div class="py-2 mx-5">
      <b-card>
        <b-row class="text-center">
          <h3>New Experiment</h3>
        </b-row>
        <!--This form contains all the necessary parameters for a user to submit a request for a experiment-->
        <b-form
          v-if="options"
          @submit="$event.preventDefault(), sendToServer()"
          @keydown.enter.prevent
          @reset="$event.preventDefault(), initSettings()"
        >
          <b-row class="text-center">
            <b-row>
              <b-col>
                <b-row>
                  <b-col md="auto" class="text-center">
                    <p>
                      Experiment type
                      <i
                        class="bi bi-info-circle"
                        v-b-tooltip.hover
                        title="Predictions are predicted ratings for known user-item pairs in the data , while recommendations are a list of recommended items for a user based on these predicted ratings."
                      >
                      </i>
                    </p>
                  </b-col>
                  <b-col md="auto">
                    <b-form-radio-group
                      v-model="form.experimentMethod"
                      :options="experimentMethods"
                    >
                    </b-form-radio-group>
                  </b-col>
                </b-row>
              </b-col>
              <!-- Input for metadata such as:
            experiment Name
            Tags (optional)
            Email for notification (optional) -->
              <b-col md="auto" class="p-2 m-1 rounded-3 bg-secondary">
                <b-row>
                  <b-col>
                    <b-form-group label-cols-md="4" label="Experiment name">
                      <b-form-input
                        placeholder="New experiment"
                        v-model="metadata.name"
                        :state="validName(metadata.name)"
                      ></b-form-input>
                    </b-form-group>
                  </b-col>
                  <b-col>
                    <b-form-group label-cols-md="4" label="E-mail (optional)">
                      <b-form-input
                        type="email"
                        placeholder="example@mail.com"
                        :state="
                          metadata.email
                            ? validateEmail(metadata.email) != null
                            : null
                        "
                        v-model="metadata.email"
                      ></b-form-input>
                    </b-form-group>
                  </b-col>
                  <b-col cols="12">
                    <b-form-group label-cols-md="2" label="Tags (optional)">
                      <Tags v-model="metadata.tags" />
                    </b-form-group>
                  </b-col>
                </b-row>
              </b-col>
            </b-row>

            <b-col class="g-0" cols="6">
              <!--User can select a dataset.-->
              <div class="p-2 my-2 mx-1 rounded-3 bg-secondary">
                <FormGroupList
                  v-model="form.lists.datasets"
                  name="dataset"
                  title="datasets"
                  :options="options.datasets"
                  required
                />
              </div>
            </b-col>

            <b-col class="g-0" cols="6">
              <!-- User can select any number of recommender approaches -->
              <div class="p-2 my-2 mx-1 rounded-3 bg-secondary">
                <FormGroupList
                  v-model="form.lists.approaches"
                  name="approach"
                  :title="
                    (form.experimentMethod == 'recommendation'
                      ? 'recommender'
                      : 'predictor') + ' approaches'
                  "
                  :options="
                    form.experimentMethod == 'recommendation'
                      ? options.recommenders
                      : options.predictors
                  "
                  :required="true"
                />

                <b-row>
                  <b-row v-if="form.experimentMethod == 'recommendation'">
                    <b-col md="auto">
                      <!--User can select the amount of recommendations per user -->
                      <b-form-group
                        label="Select number of recommendations per user: *"
                      >
                        <b-form-input
                          type="range"
                          :min="options.defaults.recCount.min"
                          :max="options.defaults.recCount.max"
                          v-model="form.recommendations"
                        />
                      </b-form-group>
                    </b-col>
                    <b-col md="auto">
                      <b-form-input md="auto" v-model="form.recommendations"
                        >{{ form.recommendations }}
                      </b-form-input>
                    </b-col>
                    <b-col md="auto">
                      <b-form-checkbox
                        v-model="form.includeRatedItems"
                        buttons
                        button-variant="outline-primary"
                        required
                      >
                        Include already rated items in
                        recommendations</b-form-checkbox
                      >
                    </b-col>
                  </b-row>
                </b-row>
              </div>
            </b-col>
            <b-row>
              <b-col>
                <!--User can select any number of metrics -->
                <div class="p-2 my-2 mx-1 rounded-3 bg-secondary">
                  <FormGroupList
                    v-model="form.lists.metrics"
                    name="metric"
                    title="metrics"
                    :maxK="form.recommendations"
                    :options="
                      form.experimentMethod == 'recommendation'
                        ? options.recMetrics
                        : options.predMetrics
                    "
                  />
                </div>
              </b-col>
              <!-- Buttons to submit or reset an experiment-->
              <div class="d-flex justify-content-center">
                <b-button class="mx-1" type="reset" variant="danger"
                  >Reset</b-button
                >
                <b-button class="mx-1" type="submit" variant="primary"
                  >Send</b-button
                >
              </div>
            </b-row>
          </b-row>
        </b-form>
        <template v-if="DEV">
          <!--Send a plethora of mock data to the queue-->
          <b-button type="test" variant="warning" @click="sendMockData(options)"
            >Mock</b-button
          >
          <!--Simple version of the mock-->
          <b-button
            type="test"
            variant="primary"
            @click="sendMockData(options, true)"
            >Simple Mock</b-button
          >
          <!--Simple version of the mock with metrics-->
          <b-button
            type="test"
            variant="primary"
            @click="sendMockData(options, true, true)"
            >Metric Mock</b-button
          >
          <!--Mock button for fast E2E Testing-->
          <b-button type="test" variant="primary" @click="form = endToEndMock"
            >E2E Mock
          </b-button>
          <!--Fill the form with mock filter options-->
          <b-button type="test" variant="primary" @click="form = filterForm"
            >Filter Mock</b-button
          >
        </template>
      </b-card>
    </div>
  </b-overlay>
</template>
