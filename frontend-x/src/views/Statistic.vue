<template>
  <div>
    <div class="mt-3 mb-3 ml-4">
      <h2>Time Consumption Statistic</h2>
    </div>
    <v-card-text>
      <!-- Overall XAI Task Time Consumption -->
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

      <!-- XAI Task Time Consumption for each Task Sheet -->
      <v-card class="mb-10" :elevation="6">
        <template v-slot:title>
          <div class="text-h6" style="float: left; line-height: 60px">
            XAI Task Time Consumption for each Task Sheet
          </div>
          <v-select
            style="width: 500px; float: right"
            label="Select Task Sheet"
            hide-details
            :items="getTaskSheetTimeSelection(xaiTaskTimeForEachSheet)"
            item-title="task_sheet_name"
            item-value="task_sheet_id"
            v-model="focusXAITaskSheetForTime"
            variant="underlined"
          ></v-select>
        </template>
        <v-divider></v-divider>
        <v-card-text>
          <div id="xaiTaskTimeForEachSheet"></div>
        </v-card-text>
      </v-card>

      <!-- Overall Evaluation Task Time Consumption -->
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

      <!-- Evaluation Task Time Consumption for each Task Sheet -->
      <v-card class="mb-10" :elevation="6">
        <template v-slot:title>
          <div class="text-h6" style="float: left; line-height: 60px">
            Evaluation Task Time Consumption for each Task Sheet
          </div>
          <v-select
            style="width: 500px; float: right"
            label="Select Task Sheet"
            hide-details
            :items="getTaskSheetTimeSelection(evalTaskTimeForEachSheet)"
            item-title="task_sheet_name"
            item-value="task_sheet_id"
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
      <!-- Global Carbon Emission -->
      <v-card class="mb-10" :elevation="6">
        <template v-slot:title>
          <div class="text-h6">
            <div>Global Carbon Emission</div>
          </div>
        </template>
        <v-divider></v-divider>
        <v-card-text>
          <v-container class="" id="wmapkey"> </v-container>
          <v-container class="mt-3" id="wmap"> </v-container>
        </v-card-text>
      </v-card>
      <!-- XAI Task Time Power & Carbon Emission -->
      <v-card class="mb-10" :elevation="6">
        <template v-slot:title>
          <div class="text-h6" style="float: left; line-height: 60px">
            <div>XAI Task Time Power & Carbon Emission</div>
          </div>
          <v-select
            style="width: 500px; float: right"
            label="Select Task Sheet"
            hide-details
            :items="getTaskSheetTimeSelection(xaiTaskSheetFinishedTaskEm)"
            item-title="task_sheet_name"
            item-value="task_sheet_id"
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
            :items="getTaskSheetTimeSelection(evalTaskSheetFinishedTaskEm)"
            item-title="task_sheet_name"
            item-value="task_sheet_id"
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
import { Choropleth, Legend, cisoMap } from "@/plugins/world-em-chart";
import { Line, Violin } from "@antv/g2plot";

function getCarouselHeight() {
  return window.innerHeight - 64 - 19.2 - 76 - 24 - 8 - 8 - 69 + "px";
}

export default {
  components: {},
  data: () => ({
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
    getTaskSheetTimeSelection(taskTimeForEachSheet) {
      const arr = [];
      for (const task_sheet_id of Object.keys(taskTimeForEachSheet)) {
        arr.push({
          task_sheet_name: taskTimeForEachSheet[task_sheet_id].task_sheet_name,
          task_sheet_id: task_sheet_id,
        });
      }
      return arr;
    },
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
        ].tasks) {
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
        ].tasks) {
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
                  task_sheet_id: task.task_sheet_id,
                  task_name: task.task_name,
                  time: t,
                };
                var d2 = {
                  ticket: task.task_ticket,
                  task_name: task.task_name,
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
                    xaiTimeDataPerSheet[task.task_sheet_id] = {
                      task_sheet_name: task.task_sheet_name,
                      tasks: [],
                    };
                  }
                  xaiTimeDataPerSheet[task.task_sheet_id].tasks.push(d2);

                  if (
                    "running_info" in task &&
                    "emission_info" in task.running_info
                  ) {
                    if (xaiEmDataPerSheet[task.task_sheet_id] === undefined) {
                      xaiEmDataPerSheet[task.task_sheet_id] = {
                        task_sheet_name: task.task_sheet_name,
                        tasks: [],
                      };
                    }
                    xaiEmDataPerSheet[task.task_sheet_id].tasks.push({
                      ticket: task.task_ticket,
                      em: task.running_info.emission_info,
                    });
                  }
                }
                if (task.task_type === "evaluation") {
                  evalData.push(d);

                  if (evalTimeDataPerSheet[task.task_sheet_id] === undefined) {
                    evalTimeDataPerSheet[task.task_sheet_id] = {
                      task_sheet_name: task.task_sheet_name,
                      tasks: [],
                    };
                  }
                  evalTimeDataPerSheet[task.task_sheet_id].tasks.push(d2);

                  if (
                    "running_info" in task &&
                    "emission_info" in task.running_info
                  ) {
                    if (evalEmDataPerSheet[task.task_sheet_id] === undefined) {
                      evalEmDataPerSheet[task.task_sheet_id] = {
                        task_sheet_name: task.task_sheet_name,
                        tasks: [],
                      };
                    }
                    evalEmDataPerSheet[task.task_sheet_id].tasks.push({
                      ticket: task.task_ticket,
                      em: task.running_info.emission_info,
                    });
                  }
                }
              }
            }

            var newCEm = [];
            var range = [0, 0];
            for (const cn of Object.keys(cem)) {
              newCEm.push({
                name: cn,
                em: cem[cn],
              });
              if (range[1] < cem[cn]) {
                range[1] = cem[cn];
              }
            }

            this.xaiTaskTimeForEachSheet = xaiTimeDataPerSheet;
            console.log(xaiTimeDataPerSheet);
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
              featureId: (d) => d.properties.name, // i.e., not ISO 3166-1 numeric
              domain: range,
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
        data: this.xaiTaskTimeForEachSheet[taskSheetId].tasks,
        padding: "auto",
        xField: "ticket",
        yField: "time",
        xAxis: {
          title: {
            text: "XAI Task Ticket (only 4 characters show)",
          },
          label: {
            formatter: (v) => {
              return v.slice(0, 4) + "...";
            },
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
        data: this.evalTaskTimeForEachSheet[taskSheetId].tasks,
        padding: "auto",
        xField: "ticket",
        yField: "time",
        xAxis: {
          title: {
            text: "Evaluation Task Ticket (only 4 characters show)",
          },
          label: {
            formatter: (v) => {
              return v.slice(0, 4) + "...";
            },
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
          label: {
            formatter: (v) => {
              return v.slice(0, 6) + "...";
            },
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
          label: {
            formatter: (v) => {
              return v.slice(0, 6) + "...";
            },
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
