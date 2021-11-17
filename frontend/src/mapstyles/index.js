import _ from 'lodash'

import bright from './bright.json'
import positron from './positron.json'

function addRoadsStyle(style, mapSource) {
  style.sources.obs = mapSource

  // insert before "road_oneway" layer
  let idx = style.layers.findIndex(l => l.id === 'road_oneway')
  if (idx === -1) {
    idx = style.layers.length
  }
  style.layers.splice(idx, 0, {
    "id": "obs",
    "type": "line",
    "source": "obs",
    "source-layer": "obs_roads",
    "layout": {
      "line-cap": "round",
      "line-join": "round"
    },
    "paint": {
      "line-width": [
        "interpolate",
        ["exponential", 1.5],
        ["zoom"],
        12,
        1,
        17,
        [
          "case",
          [
            "!",
            [
              "to-boolean",
              [
                "get",
                "distance_overtaker_mean"
              ]
            ]
          ],
          2,
          6
        ]
      ],
      "line-color": [
        "case",
        [
          "!",
          [
            "to-boolean",
            [
              "get",
              "distance_overtaker_mean"
            ]
          ]
        ],
        "#ABC",
        [
          "interpolate-hcl",
          ["linear"],
          [
            "get",
            "distance_overtaker_mean"
          ],
          1,
          "rgba(255, 0, 0, 1)",
          1.3,
          "rgba(255, 200, 0, 1)",
          1.5,
          "rgba(67, 200, 0, 1)",
          1.7,
          "rgba(67, 150, 0, 1)"
        ]
      ],
      "line-opacity": [
        "interpolate",
        ["linear"],
        ["zoom"],
        12,
        0,
        13,
        [
          "case",
          [
            "!",
            [
              "to-boolean",
              [
                "get",
                "distance_overtaker_mean"
              ]
            ]
          ],
          0,
          1
        ],
        14,
        [
          "case",
          [
            "!",
            [
              "to-boolean",
              [
                "get",
                "distance_overtaker_mean"
              ]
            ]
          ],
          0,
          1
        ],
        15,
        1
      ],
      "line-offset": [
        "interpolate",
        ["exponential", 1.5],
        ["zoom"],
        12,
        ["get", "offset_direction"],
        19,
        [
          "*",
          ["get", "offset_direction"],
          8
        ]
      ]
    },
    "minzoom": 12
  })

  return style
}


export const basemap = bright
export const obsRoads = (sourceUrl) => addRoadsStyle(_.cloneDeep(positron), sourceUrl)