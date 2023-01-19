<template>
  <div>
    <div class="mt-3 mb-3 ml-4">
      <h2>Time Consumption Statistic</h2>
    </div>
    <v-card-text>
      <v-card class="mb-10" :elevation="6">
        <template v-slot:title>
          <div class="clearfix">
            <div>Overall XAI Task Time Consumption</div>
          </div>
        </template>
        <v-divider></v-divider>
        <v-card-text>
          <div id="xaiTaskSheetFinishedTaskTimeViolin"></div>
        </v-card-text>
      </v-card>

      <v-card class="mb-10" :elevation="6">
        <template v-slot:title>
          <div class="text-h6" style="float: left; line-height: 60px">
            XAI Task Time Consumption for each Task Sheet
          </div>
          <v-select
            style="width: 500px; float: right"
            label="Select Task Sheet"
            hide-details
            :items="Object.keys(xaiTaskTimeForEachSheet)"
            v-model="focusXAITaskSheetForTime"
            variant="underlined"
          ></v-select>
        </template>
        <v-divider></v-divider>
        <v-card-text>
          <div id="xaiTaskTimeForEachSheet"></div>
        </v-card-text>
      </v-card>

      <v-card class="mb-10" :elevation="6">
        <template v-slot:title>
          <div class="clearfix">
            <div>Overall Evaluation Task Time Consumption</div>
          </div>
        </template>
        <v-divider></v-divider>
        <v-card-text>
          <div id="evalTaskSheetFinishedTaskTimeViolin"></div>
        </v-card-text>
      </v-card>

      <v-card class="mb-10" :elevation="6">
        <template v-slot:title>
          <div class="text-h6" style="float: left; line-height: 60px">
            Evaluation Task Time Consumption for each Task Sheet
          </div>
          <v-select
            style="width: 500px; float: right"
            label="Select Task Sheet"
            hide-details
            :items="Object.keys(evalTaskTimeForEachSheet)"
            v-model="focusEvalTaskSheetForTime"
            variant="underlined"
          ></v-select>
        </template>
        <v-divider></v-divider>
        <v-card-text>
          <div id="evalTaskTimeForEachSheet"></div>
        </v-card-text>
      </v-card>
    </v-card-text>
    <v-divider></v-divider>
    <div class="mt-12 mb-3 ml-4">
      <h2>Power & Carbon Emission Statistic</h2>
    </div>
    <v-card-text>
      <v-card class="mb-10" :elevation="6">
        <template v-slot:title>
          <div class="text-h6">
            <div>Global Carbon Emission</div>
          </div>
        </template>
        <v-divider></v-divider>
        <v-card-text>
          <v-container class="pa-0" id="wmapkey"> </v-container>
          <v-container class="pa-0 mt-3" id="wmap"> </v-container>
        </v-card-text>
      </v-card>
      <v-card class="mb-10" :elevation="6">
        <template v-slot:title>
          <div class="text-h6" style="float: left; line-height: 60px">
            <div>XAI Task Time Power & Carbon Emission</div>
          </div>
          <v-select
            style="width: 500px; float: right"
            label="Select Task Sheet"
            hide-details
            :items="Object.keys(xaiTaskSheetFinishedTaskEm)"
            v-model="focusXAITaskSheetForEm"
            variant="underlined"
          ></v-select>
        </template>
        <v-divider></v-divider>
        <v-card-text>
          <v-container class="pa-0">
            <v-row no-gutters>
              <v-col>
                <v-sheet class="pa-2">
                  Infrastructure Host at:
                  <span class="text-green-lighten-1 font-weight-bold">{{
                    getFocusXAITaskSheetForEmSt().host +
                    " | " +
                    cisoMap[getFocusXAITaskSheetForEmSt().host]["name"]
                  }}</span>
                </v-sheet>
              </v-col>
              <v-col>
                <v-sheet class="pa-2 text-right"> </v-sheet>
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col>
                <v-sheet class="pa-2">
                  Power Consumption of All Tasks:
                  <span class="text-green-lighten-1 font-weight-bold">{{
                    getFocusXAITaskSheetForEmSt().powerOfAllTask.toFixed(10) +
                    " kWh "
                  }}</span>
                </v-sheet>
              </v-col>
              <v-col>
                <v-sheet class="pa-2 text-right">
                  Power Consumption of Last Task:
                  <span class="text-green-lighten-1 font-weight-bold">{{
                    getFocusXAITaskSheetForEmSt().lastPower.toFixed(10) +
                    " kWh "
                  }}</span></v-sheet
                >
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col>
                <v-sheet class="pa-2">
                  Carbon Equivalent of All Tasks:
                  <span class="text-green-lighten-1 font-weight-bold">{{
                    getFocusXAITaskSheetForEmSt().carbonEmOfAllTask.toFixed(
                      10
                    ) + " kg "
                  }}</span>
                </v-sheet>
              </v-col>
              <v-col>
                <v-sheet class="pa-2 text-right">
                  Carbon Equivalent of Last Task:
                  <span class="text-green-lighten-1 font-weight-bold">{{
                    getFocusXAITaskSheetForEmSt().lastCarbonEm.toFixed(10) +
                    " kg "
                  }}</span>
                </v-sheet>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
      </v-card>

      <v-card class="mb-10" :elevation="6">
        <template v-slot:title>
          <div class="text-h6" style="float: left; line-height: 60px">
            <div>Evaluation Task Time Power & Carbon Emission</div>
          </div>
          <v-select
            style="width: 500px; float: right"
            label="Select Task Sheet"
            hide-details
            :items="Object.keys(evalTaskSheetFinishedTaskEm)"
            v-model="focusEvalTaskSheetForEm"
            variant="underlined"
          ></v-select>
        </template>
        <v-divider></v-divider>
        <v-card-text>
          <v-container class="pa-0">
            <v-row no-gutters>
              <v-col>
                <v-sheet class="pa-2">
                  Infrastructure Host at:
                  <span class="text-green-lighten-1 font-weight-bold">{{
                    getFocusEvalTaskSheetForEmSt().host +
                    " | " +
                    cisoMap[getFocusEvalTaskSheetForEmSt().host]["name"]
                  }}</span>
                </v-sheet>
              </v-col>
              <v-col>
                <v-sheet class="pa-2 text-right"> </v-sheet>
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col>
                <v-sheet class="pa-2">
                  Power Consumption of All Tasks:
                  <span class="text-green-lighten-1 font-weight-bold">{{
                    getFocusEvalTaskSheetForEmSt().powerOfAllTask.toFixed(10) +
                    " kWh "
                  }}</span>
                </v-sheet>
              </v-col>
              <v-col>
                <v-sheet class="pa-2 text-right">
                  Power Consumption of Last Task:
                  <span class="text-green-lighten-1 font-weight-bold">{{
                    getFocusEvalTaskSheetForEmSt().lastPower.toFixed(10) +
                    " kWh "
                  }}</span></v-sheet
                >
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col>
                <v-sheet class="pa-2">
                  Carbon Equivalent of All Tasks:
                  <span class="text-green-lighten-1 font-weight-bold">{{
                    getFocusEvalTaskSheetForEmSt().carbonEmOfAllTask.toFixed(
                      10
                    ) + " kg "
                  }}</span>
                </v-sheet>
              </v-col>
              <v-col>
                <v-sheet class="pa-2 text-right">
                  Carbon Equivalent of Last Task:
                  <span class="text-green-lighten-1 font-weight-bold">{{
                    getFocusEvalTaskSheetForEmSt().lastCarbonEm.toFixed(10) +
                    " kg "
                  }}</span>
                </v-sheet>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
      </v-card>
    </v-card-text>
  </div>
</template>

<script>
import ciso from "@/assets/con-iso-code-a3.json";
import * as d3 from "d3";
import world from "@/assets/countries-50m.json";
import * as topojson from "topojson-client";

// Copyright 2021, Observable Inc.
// Released under the ISC license.
// https://observablehq.com/@d3/color-legend
function Legend(
  color,
  {
    title,
    tickSize = 6,
    width = 320,
    height = 44 + tickSize,
    marginTop = 18,
    marginRight = 0,
    marginBottom = 16 + tickSize,
    marginLeft = 0,
    ticks = width / 64,
    tickFormat,
    tickValues,
  } = {}
) {
  function ramp(color, n = 256) {
    const canvas = document.createElement("canvas");
    canvas.width = n;
    canvas.height = 1;
    const context = canvas.getContext("2d");
    for (let i = 0; i < n; ++i) {
      context.fillStyle = color(i / (n - 1));
      context.fillRect(i, 0, 1, 1);
    }
    return canvas;
  }

  const svg = d3
    .create("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [0, 0, width, height])
    .style("overflow", "visible")
    .style("display", "block");

  let tickAdjust = (g) =>
    g.selectAll(".tick line").attr("y1", marginTop + marginBottom - height);
  let x;

  // Continuous
  if (color.interpolate) {
    const n = Math.min(color.domain().length, color.range().length);

    x = color
      .copy()
      .rangeRound(
        d3.quantize(d3.interpolate(marginLeft, width - marginRight), n)
      );

    svg
      .append("image")
      .attr("x", marginLeft)
      .attr("y", marginTop)
      .attr("width", width - marginLeft - marginRight)
      .attr("height", height - marginTop - marginBottom)
      .attr("preserveAspectRatio", "none")
      .attr(
        "xlink:href",
        ramp(
          color.copy().domain(d3.quantize(d3.interpolate(0, 1), n))
        ).toDataURL()
      );
  }

  // Sequential
  else if (color.interpolator) {
    x = Object.assign(
      color
        .copy()
        .interpolator(d3.interpolateRound(marginLeft, width - marginRight)),
      {
        range() {
          return [marginLeft, width - marginRight];
        },
      }
    );

    svg
      .append("image")
      .attr("x", marginLeft)
      .attr("y", marginTop)
      .attr("width", width - marginLeft - marginRight)
      .attr("height", height - marginTop - marginBottom)
      .attr("preserveAspectRatio", "none")
      .attr("xlink:href", ramp(color.interpolator()).toDataURL());

    // scaleSequentialQuantile doesn’t implement ticks or tickFormat.
    if (!x.ticks) {
      if (tickValues === undefined) {
        const n = Math.round(ticks + 1);
        tickValues = d3
          .range(n)
          .map((i) => d3.quantile(color.domain(), i / (n - 1)));
      }
      if (typeof tickFormat !== "function") {
        tickFormat = d3.format(tickFormat === undefined ? ",f" : tickFormat);
      }
    }
  }

  // Threshold
  else if (color.invertExtent) {
    const thresholds = color.thresholds
      ? color.thresholds() // scaleQuantize
      : color.quantiles
      ? color.quantiles() // scaleQuantile
      : color.domain(); // scaleThreshold

    const thresholdFormat =
      tickFormat === undefined
        ? (d) => d
        : typeof tickFormat === "string"
        ? d3.format(tickFormat)
        : tickFormat;

    x = d3
      .scaleLinear()
      .domain([-1, color.range().length - 1])
      .rangeRound([marginLeft, width - marginRight]);

    svg
      .append("g")
      .selectAll("rect")
      .data(color.range())
      .join("rect")
      .attr("x", (d, i) => x(i - 1))
      .attr("y", marginTop)
      .attr("width", (d, i) => x(i) - x(i - 1))
      .attr("height", height - marginTop - marginBottom)
      .attr("fill", (d) => d);

    tickValues = d3.range(thresholds.length);
    tickFormat = (i) => thresholdFormat(thresholds[i], i);
  }

  // Ordinal
  else {
    x = d3
      .scaleBand()
      .domain(color.domain())
      .rangeRound([marginLeft, width - marginRight]);

    svg
      .append("g")
      .selectAll("rect")
      .data(color.domain())
      .join("rect")
      .attr("x", x)
      .attr("y", marginTop)
      .attr("width", Math.max(0, x.bandwidth() - 1))
      .attr("height", height - marginTop - marginBottom)
      .attr("fill", color);

    tickAdjust = () => {};
  }

  svg
    .append("g")
    .attr("transform", `translate(0,${height - marginBottom})`)
    .call(
      d3
        .axisBottom(x)
        .ticks(ticks, typeof tickFormat === "string" ? tickFormat : undefined)
        .tickFormat(typeof tickFormat === "function" ? tickFormat : undefined)
        .tickSize(tickSize)
        .tickValues(tickValues)
    )
    .call(tickAdjust)
    .call((g) => g.select(".domain").remove())
    .call((g) =>
      g
        .append("text")
        .attr("x", marginLeft)
        .attr("y", marginTop + marginBottom - height - 6)
        .attr("fill", "currentColor")
        .attr("text-anchor", "start")
        .attr("font-weight", "bold")
        .attr("class", "title")
        .text(title)
    );

  return svg.node();
}

// Copyright 2021 Observable, Inc.
// Released under the ISC license.
// https://observablehq.com/@d3/choropleth
function Choropleth(
  data,
  {
    id = (d) => d.id, // given d in data, returns the feature id
    value = () => undefined, // given d in data, returns the quantitative value
    title, // given a feature f and possibly a datum d, returns the hover text
    format, // optional format specifier for the title
    scale = d3.scaleSequential, // type of color scale
    domain, // [min, max] values; input of color scale
    range = d3.interpolateBlues, // output of color scale
    width = 640, // outer width, in pixels
    height, // outer height, in pixels
    projection, // a D3 projection; null for pre-projected geometry
    features, // a GeoJSON feature collection
    featureId = (d) => d.id, // given a feature, returns its id
    borders, // a GeoJSON object for stroking borders
    outline = projection && projection.rotate ? { type: "Sphere" } : null, // a GeoJSON object for the background
    unknown = "#ccc", // fill color for missing data
    fill = "white", // fill color for outline
    stroke = "white", // stroke color for borders
    strokeLinecap = "round", // stroke line cap for borders
    strokeLinejoin = "round", // stroke line join for borders
    strokeWidth, // stroke width for borders
    strokeOpacity, // stroke opacity for borders
  } = {}
) {
  // Compute values.
  const N = d3.map(data, id);
  const V = d3.map(data, value).map((d) => (d == null ? NaN : +d));
  const Im = new d3.InternMap(N.map((id, i) => [id, i]));
  const If = d3.map(features.features, featureId);

  // Compute default domains.
  if (domain === undefined) domain = d3.extent(V);

  // Construct scales.
  const color = scale(domain, range);
  if (color.unknown && unknown !== undefined) color.unknown(unknown);

  // Compute titles.
  if (title === undefined) {
    format = color.tickFormat(100, format);
    title = (f, i) => `${f.properties.name}\n${format(V[i])}`;
  } else if (title !== null) {
    const T = title;
    const O = d3.map(data, (d) => d);
    title = (f, i) => T(f, O[i]);
  }

  // Compute the default height. If an outline object is specified, scale the projection to fit
  // the width, and then compute the corresponding height.
  if (height === undefined) {
    if (outline === undefined) {
      height = 400;
    } else {
      const [[x0, y0], [x1, y1]] = d3
        .geoPath(projection.fitWidth(width, outline))
        .bounds(outline);
      const dy = Math.ceil(y1 - y0),
        l = Math.min(Math.ceil(x1 - x0), dy);
      projection.scale((projection.scale() * (l - 1)) / l).precision(0.2);
      height = dy;
    }
  }

  // Construct a path generator.
  const path = d3.geoPath(projection);

  const svg = d3
    .create("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [0, 0, width, height])
    .attr("style", "width: 100%; height: auto; height: intrinsic;");

  if (outline != null)
    svg
      .append("path")
      .attr("fill", fill)
      .attr("stroke", "currentColor")
      .attr("d", path(outline));

  svg
    .append("g")
    .selectAll("path")
    .data(features.features)
    .join("path")
    .attr("fill", (d, i) => color(V[Im.get(If[i])]))
    .attr("d", path)
    .append("title")
    .text((d, i) => title(d, Im.get(If[i])));

  if (borders != null)
    svg
      .append("path")
      .attr("pointer-events", "none")
      .attr("fill", "none")
      .attr("stroke", stroke)
      .attr("stroke-linecap", strokeLinecap)
      .attr("stroke-linejoin", strokeLinejoin)
      .attr("stroke-width", strokeWidth)
      .attr("stroke-opacity", strokeOpacity)
      .attr("d", path(borders));

  return Object.assign(svg.node(), { scales: { color } });
}

var rename = new Map([
  ["Antigua and Barbuda", "Antigua and Barb."],
  ["Bolivia (Plurinational State of)", "Bolivia"],
  ["Bosnia and Herzegovina", "Bosnia and Herz."],
  ["Brunei Darussalam", "Brunei"],
  ["Central African Republic", "Central African Rep."],
  ["Cook Islands", "Cook Is."],
  ["Democratic People's Republic of Korea", "North Korea"],
  ["Democratic Republic of the Congo", "Dem. Rep. Congo"],
  ["Dominican Republic", "Dominican Rep."],
  ["Equatorial Guinea", "Eq. Guinea"],
  ["Iran (Islamic Republic of)", "Iran"],
  ["Lao People's Democratic Republic", "Laos"],
  ["Marshall Islands", "Marshall Is."],
  ["Micronesia (Federated States of)", "Micronesia"],
  ["Republic of Korea", "South Korea"],
  ["Republic of Moldova", "Moldova"],
  ["Russian Federation", "Russia"],
  ["Saint Kitts and Nevis", "St. Kitts and Nevis"],
  ["Saint Vincent and the Grenadines", "St. Vin. and Gren."],
  ["Sao Tome and Principe", "São Tomé and Principe"],
  ["Solomon Islands", "Solomon Is."],
  ["South Sudan", "S. Sudan"],
  ["Swaziland", "eSwatini"],
  ["Syrian Arab Republic", "Syria"],
  ["The former Yugoslav Republic of Macedonia", "Macedonia"],
  // ["Tuvalu", ?],
  ["United Republic of Tanzania", "Tanzania"],
  ["Venezuela (Bolivarian Republic of)", "Venezuela"],
  ["Viet Nam", "Vietnam"],
]);

var countries = topojson.feature(world, world.objects.countries);
var countrymesh = topojson.mesh(
  world,
  world.objects.countries,
  (a, b) => a !== b
);

const cisoMap = {};

for (const cis of ciso) {
  cisoMap[cis.code] = cis;
}

cisoMap["nowhere"] = {
  name: "nowhere",
};

function getCarouselHeight() {
  return window.innerHeight - 64 - 19.2 - 76 - 24 - 8 - 8 - 69 + "px";
}

import { Line, Violin } from "@antv/g2plot";

export default {
  components: {},
  data: () => ({
    countries,
    countrymesh,
    rename,
    cisoMap,
    carouselHeight: getCarouselHeight(),
    xaiTaskTimeForEachSheet: {},
    evalTaskTimeForEachSheet: {},
    xaiTaskSheetFinishedTaskTime: [],
    xaiTaskSheetFinishedTaskEm: [],
    evalTaskSheetFinishedTaskTime: [],
    evalTaskSheetFinishedTaskEm: [],
    focusXAITaskSheetForTime: undefined,
    focusXAITaskSheetForEm: undefined,
    focusEvalTaskSheetForTime: undefined,
    focusEvalTaskSheetForEm: undefined,
    linex: undefined,
    linee: undefined,
    violinPlotx: undefined,
    violinPlote: undefined,
  }),
  computed: {},
  watch: {
    focusXAITaskSheetForTime(n, o) {
      if (o !== undefined) {
        this.renderXaiTaskTimeForEachSheet(n);
      }
    },
    focusEvalTaskSheetForTime(n, o) {
      if (o !== undefined) {
        this.renderEvalTaskTimeForEachSheet(n);
      }
    },
  },
  methods: {
    getFocusXAITaskSheetForEmSt() {
      const st = {
        host: "nowhere",
        carbonEmOfAllTask: 0,
        powerOfAllTask: 0,
        lastCarbonEm: 0,
        lastPower: 0,
      };
      if (this.focusXAITaskSheetForEm !== undefined) {
        for (const em of this.xaiTaskSheetFinishedTaskEm[
          this.focusXAITaskSheetForEm
        ]) {
          st.carbonEmOfAllTask += em.em.emissions;
          st.powerOfAllTask += em.em.energy_consumed;
          st.host = em.em.country_iso_code;

          st.lastCarbonEm = em.em.emissions;
          st.lastPower = em.em.energy_consumed;
        }
      }
      return st;
    },
    getFocusEvalTaskSheetForEmSt() {
      const st = {
        host: "nowhere",
        carbonEmOfAllTask: 0,
        powerOfAllTask: 0,
        lastCarbonEm: 0,
        lastPower: 0,
      };
      if (this.focusEvalTaskSheetForEm !== undefined) {
        for (const em of this.evalTaskSheetFinishedTaskEm[
          this.focusEvalTaskSheetForEm
        ]) {
          st.carbonEmOfAllTask += em.em.emissions;
          st.powerOfAllTask += em.em.energy_consumed;
          st.host = em.em.country_iso_code;

          st.lastCarbonEm = em.em.emissions;
          st.lastPower = em.em.energy_consumed;
        }
      }
      return st;
    },
    fetchTasks(cb) {
      this.ax.get(
        "http://127.0.0.1:5006/task_publisher/task",
        {},
        {
          success: (response) => {
            var xaiData = [];
            var evalData = [];
            var xaiTimeDataPerSheet = {};
            var evalTimeDataPerSheet = {};
            var xaiEmDataPerSheet = {};
            var evalEmDataPerSheet = {};

            var cem = {};
            for (const task of response.data) {
              if (task.task_status === "finished") {
                var t = Number((task.end_time - task.start_time).toFixed(2));
                var d = {
                  task_sheet_id: task.task_sheet_id.slice(0, 6) + "...",
                  time: t,
                };
                var d2 = {
                  ticket: task.task_ticket.slice(0, 4) + "...",
                  time: t,
                };
                if (
                  "running_info" in task &&
                  "emission_info" in task.running_info
                ) {
                  if (
                    cem[task.running_info.emission_info.country_name] ===
                    undefined
                  ) {
                    cem[task.running_info.emission_info.country_name] = 0;
                  }
                  cem[task.running_info.emission_info.country_name] +=
                    task.running_info.emission_info.energy_consumed;
                }
                if (task.task_type === "xai") {
                  xaiData.push(d);

                  if (xaiTimeDataPerSheet[task.task_sheet_id] === undefined) {
                    xaiTimeDataPerSheet[task.task_sheet_id] = [];
                  }
                  xaiTimeDataPerSheet[task.task_sheet_id].push(d2);

                  if (
                    "running_info" in task &&
                    "emission_info" in task.running_info
                  ) {
                    if (xaiEmDataPerSheet[task.task_sheet_id] === undefined) {
                      xaiEmDataPerSheet[task.task_sheet_id] = [];
                    }
                    xaiEmDataPerSheet[task.task_sheet_id].push({
                      ticket: task.task_ticket.slice(0, 4) + "...",
                      em: task.running_info.emission_info,
                    });
                  }
                }
                if (task.task_type === "evaluation") {
                  evalData.push(d);

                  if (evalTimeDataPerSheet[task.task_sheet_id] === undefined) {
                    evalTimeDataPerSheet[task.task_sheet_id] = [];
                  }
                  evalTimeDataPerSheet[task.task_sheet_id].push(d2);

                  if (
                    "running_info" in task &&
                    "emission_info" in task.running_info
                  ) {
                    if (evalEmDataPerSheet[task.task_sheet_id] === undefined) {
                      evalEmDataPerSheet[task.task_sheet_id] = [];
                    }
                    evalEmDataPerSheet[task.task_sheet_id].push({
                      ticket: task.task_ticket.slice(0, 4) + "...",
                      em: task.running_info.emission_info,
                    });
                  }
                }
              }
            }

            var newCEm = [];
            for (const cn of Object.keys(cem)) {
              newCEm.push({
                name: cn,
                em: cem[cn],
              });
            }

            this.xaiTaskTimeForEachSheet = xaiTimeDataPerSheet;
            this.evalTaskTimeForEachSheet = evalTimeDataPerSheet;

            this.xaiTaskSheetFinishedTaskTime = xaiData;
            this.xaiTaskSheetFinishedTaskEm = xaiEmDataPerSheet;

            this.evalTaskSheetFinishedTaskTime = evalData;
            this.evalTaskSheetFinishedTaskEm = evalEmDataPerSheet;

            const xaiEmDataPerSheetKeys = Object.keys(xaiEmDataPerSheet);
            if (xaiEmDataPerSheetKeys.length > 0) {
              this.focusXAITaskSheetForEm = xaiEmDataPerSheetKeys[0];
            }

            const evalEmDataPerSheetKeys = Object.keys(evalEmDataPerSheet);
            if (evalEmDataPerSheetKeys.length > 0) {
              this.focusEvalTaskSheetForEm = evalEmDataPerSheetKeys[0];
            }

            var chart = Choropleth(newCEm, {
              id: (d) => d.name, // country name, e.g. Zimbabwe
              value: (d) => d.em, // health-adjusted life expectancy
              range: d3.interpolateYlGnBu,
              features: countries,
              featureId: (d) => d.properties.name, // i.e., not ISO 3166-1 numeric
              borders: countrymesh,
              projection: d3.geoEqualEarth(),
            });
            document.getElementById("wmap").appendChild(chart);

            var key = Legend(chart.scales.color, {
              title: "Carbon Emission (kg)",
            });

            document.getElementById("wmapkey").appendChild(key);
            if (cb !== undefined) {
              cb();
            }
          },
          error: (e) => {
            console.log(e);
          },
          final: () => {
            // console.log(JSON.parse(JSON.stringify(this.provenance)));
          },
        }
      );
    },
    renderXaiTaskTimeForEachSheet(taskSheetId) {
      this.focusXAITaskSheetForTime = taskSheetId;
      if (this.linex !== undefined) {
        this.linex.destroy();
      }
      this.linex = new Line("xaiTaskTimeForEachSheet", {
        data: this.xaiTaskTimeForEachSheet[taskSheetId],
        padding: "auto",
        xField: "ticket",
        yField: "time",
        xAxis: {
          title: {
            text: "XAI Task Ticket (only 4 characters show)",
          },
        },
        yAxis: {
          title: {
            text: "Task Time Consumption (seconds)",
          },
        },
        smooth: true,
      });
      this.linex.render();
    },
    renderEvalTaskTimeForEachSheet(taskSheetId) {
      this.focusEvalTaskSheetForTime = taskSheetId;
      if (this.linee !== undefined) {
        this.linee.destroy();
      }
      this.linee = new Line("evalTaskTimeForEachSheet", {
        data: this.evalTaskTimeForEachSheet[taskSheetId],
        padding: "auto",
        xField: "ticket",
        yField: "time",
        xAxis: {
          title: {
            text: "Evaluation Task Ticket (only 4 characters show)",
          },
        },
        yAxis: {
          title: {
            text: "Task Time Consumption (seconds)",
          },
        },
        smooth: true,
      });
      this.linee.render();
    },
    renderStat() {
      this.violinPlotx = new Violin("xaiTaskSheetFinishedTaskTimeViolin", {
        data: this.xaiTaskSheetFinishedTaskTime,
        xField: "task_sheet_id",
        yField: "time",
        yAxis: {
          title: {
            text: "Task Time Consumption (seconds)",
          },
        },
        xAxis: {
          title: {
            text: "XAI Task Sheet ID (only 6 characters show)",
          },
        },
      });
      const firstXaiTaskSheet = Object.keys(this.xaiTaskTimeForEachSheet)[0];
      this.renderXaiTaskTimeForEachSheet(firstXaiTaskSheet);

      this.violinPlotx.render();
      this.violinPlote = new Violin("evalTaskSheetFinishedTaskTimeViolin", {
        data: this.evalTaskSheetFinishedTaskTime,
        xField: "task_sheet_id",
        yField: "time",
        yAxis: {
          title: {
            text: "Task Time Consumption (seconds)",
          },
        },
        xAxis: {
          title: {
            text: "Evaluation Task Sheet ID (only 6 characters show)",
          },
        },
      });
      this.violinPlote.render();
      const firstEvalTaskSheet = Object.keys(this.evalTaskTimeForEachSheet)[0];
      this.renderEvalTaskTimeForEachSheet(firstEvalTaskSheet);
    },
  },

  mounted: function () {
    const thiz = this;
    window.addEventListener("resize", (e) => {
      thiz.carouselHeight = getCarouselHeight();
    });
    setTimeout(() => {
      thiz.carouselHeight = getCarouselHeight();
    }, 200);
    this.fetchTasks(this.renderStat);
  },
  unmounted: function () {
    if (this.linex !== undefined) {
      this.linex.destroy();
    }
    if (this.violinPlote !== undefined) {
      this.violinPlote.destroy();
    }
    if (this.violinPlotx !== undefined) {
      this.violinPlotx.destroy();
    }
  },
};
</script>

<style></style>
