/*This program has been developed by students from the bachelor Computer Science at
Utrecht University within the Software Project course.
© Copyright Utrecht University (Department of Information and Computing Sciences)*/

import {
  formatResults,
  formatMultipleItems,
  formatResult,
  showDatasetInfo,
  formatMetric,
  formatEvaluation,
} from '../helpers/resultFormatter'

/**
 * Test the formatting of all results
 */
describe('format results', () => {
  // Test a formatted version of an empty array to be empty
  test('empty', () => {
    expect(formatResults([]).length).toBe(0)
  })
  // TODO
})

/**
 * Test the string formatting of an array of items
 */
describe('format multiple items', () => {
  // Test that an empty array gives an empty string
  test('empty', () => {
    expect(formatMultipleItems([])).toBe('')
  })

  // Test that a null array gives None
  test('undefined', () => {
    expect(formatMultipleItems(null)).toBe('None')
  })

  const items = [{ name: 'a' }, { name: 'b' }]
  test('single item', () => {
    expect(formatMultipleItems([items[0]])).toBe(items[0].name)
  })

  test('multiple items', () => {
    expect(formatMultipleItems(items)).toBe('a, b')
  })
})

/*
describe('format result', () => {
  // TODO
  //test('', () => {})
})*/

/**
 * Test the short string description of a dataset
 */
describe('show dataset info', () => {
  // A dataset without parmeters should just show the dataset name
  test('no parameter', () => {
    const dataset = { name: 'foo' }
    expect(showDatasetInfo(dataset)).toBe('Dataset: ' + dataset.name)
  })

  // A dataset with parameters should show both name and parameters
  test('parameter', () => {
    const dataset = { name: 'foo', parameter: 'bar' }
    expect(showDatasetInfo(dataset)).toBe(
      'Dataset: ' + dataset.name + 'with parameters ' + dataset.parameter
    )
  })
})

/*
describe('format evaluation', () => {
  //TODO
  //test('', () => {})
})*/

/**
 * Test string formatting (new name) of a metric
 */
describe('format metric', () => {
  // A metric with parameters (k) should show both name and parameters
  test('k metric', () => {
    const metric = { name: 'foo k', params: [{ value: 0 }] }
    expect(formatMetric(metric)).toBe('foo 0')
  })
  // A metric without parameters should just show its name
  test('no parameter metric', () => {
    expect(formatMetric({ name: 'foo' })).toBe('foo')
  })
})
