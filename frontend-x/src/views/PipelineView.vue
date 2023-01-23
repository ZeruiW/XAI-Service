<template>
  <v-card class="mx-auto" style="height: 100%" :elevation="3">
    <template v-slot:title>
      <div class="clearfix">
        <div style="width: 50%; float: left; padding: 0.1em">
          Created Pipeline
        </div>
        <div
          style="width: 50%; float: right; text-align: right; padding: 0.1em"
        >
          <v-btn size="small" color="success" @click="openD()">
            Add Pipeline
          </v-btn>
        </div>
      </div>
    </template>

    <v-divider></v-divider>
    <!-- <v-card-text> This is content </v-card-text> -->
    <v-table>
      <colgroup>
        <col span="1" style="width: 20%" />
        <col span="1" style="width: 10%" />
        <col span="1" style="width: 20%" />
        <col span="1" style="width: 20%" />
        <col span="1" style="width: 30%" />
      </colgroup>
      <thead>
        <tr>
          <th class="text-left font-weight-bold">ID</th>
          <th class="text-left font-weight-bold">Name</th>
          <th class="text-left font-weight-bold">XAI Task Sheet ID</th>
          <th class="text-left font-weight-bold">Eval Task Sheet ID</th>
          <th class="text-left font-weight-bold"></th>
        </tr>
      </thead>
      <tbody>
        <tr class="trHover" v-for="item in pipelines" :key="item.pipeline_id">
          <td>{{ item.pipeline_id }}</td>
          <td>{{ item.pipeline_name }}</td>
          <td>
            {{ item.xai_task_sheet_id }}
          </td>
          <td>
            {{ item.evaluation_task_sheet_id }}
          </td>
          <td style="text-align: right">
            <v-btn
              color="blue"
              size="x-small"
              prepend-icon="mdi-television"
              @click="openD(item)"
              >Detail</v-btn
            >
            <v-btn
              style="margin-left: 0.5em"
              color="success"
              size="x-small"
              prepend-icon="mdi-play"
              @click="openPRLD(item)"
              >Runs</v-btn
            >
            <v-btn
              style="margin-left: 0.5em"
              color="error"
              size="x-small"
              prepend-icon="mdi-delete"
              @click="deletePipeline(item)"
              >Delete</v-btn
            >
          </td>
        </tr>
      </tbody>
    </v-table>

    <!-- add pipeline  -->
    <v-dialog
      id="pipeline-create-dialog"
      contained
      v-model="dialog"
      max-width="600px"
      persistent
    >
      <v-form
        id="pipeline-create-form"
        ref="form"
        v-model="valid"
        lazy-validation
        @submit="submitAddPipelineAction"
        :disabled="disabled"
      >
        <v-card>
          <v-card-title>
            <span v-if="!disabled" class="text-h5">Pipeline</span>
            <span v-if="disabled" class="text-h5">Pipeline Detail</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-text-field
                  label="Pipeline Name*"
                  name="pipeline_name"
                  v-model="current_pipeline.pipeline_name"
                  :rules="[(v) => !!v || 'Name is required']"
                  :readonly="disabled"
                  required
                  density="compact"
                ></v-text-field>
              </v-row>
              <!-- xai -->
              <v-row>
                <v-select
                  label="XAI Task Sheet Name"
                  :items="xaiTaskSheetList"
                  item-title="task_sheet_name"
                  item-value="task_sheet_id"
                  name="current_xai_task_sheet_id"
                  v-model="current_pipeline.xai_task_sheet_id"
                  :rules="[(v) => !!v || 'This field is required']"
                  ref="current_xai_task_sheet_id"
                  :readonly="disabled"
                  hide-details
                  density="compact"
                ></v-select>
              </v-row>

              <!-- eval -->
              <v-row class="mt-8">
                <v-select
                  label="Evaluation Task Sheet Name"
                  :items="evalTaskSheetList"
                  item-title="task_sheet_name"
                  item-value="task_sheet_id"
                  name="current_evaluation_task_sheet_id"
                  v-model="current_pipeline.evaluation_task_sheet_id"
                  :rules="[(v) => !!v || 'This field is required']"
                  ref="current_evaluation_task_sheet_id"
                  :readonly="disabled"
                  hide-details
                  density="compact"
                ></v-select>
              </v-row>
            </v-container>
            <small v-if="!disabled">*indicates required field</small>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="red-darken-1" @click="closeD"> Close </v-btn>
            <v-btn
              v-if="!disabled"
              type="submit"
              color="green-darken-1"
              form="pipeline-create-form"
            >
              Submit
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-form>
    </v-dialog>

    <!-- pipeline run list  -->
    <v-dialog
      id="pipeline-run-list-dialog"
      contained
      style="height: 100%"
      v-model="prldialog"
      persistent
    >
      <v-card style="height: 100000px">
        <v-card-title>
          <v-card-actions>
            <span class="text-h5"
              >Pipeline Run: {{ current_pipeline.pipeline_name }}</span
            >
            <v-spacer></v-spacer>
            <v-btn
              size="small"
              variant="outlined"
              color="green-darken-1"
              form="task-sheet-create-form"
              @click="runCurrentPipeline"
            >
              Run
            </v-btn>
            <v-btn
              size="small"
              variant="outlined"
              color="red-darken-1"
              @click="closePRLD"
            >
              Close
            </v-btn>
          </v-card-actions>
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text>
          <v-table>
            <colgroup>
              <col span="1" style="width: 10%" />
              <col span="1" style="width: 25%" />
              <col span="1" style="width: 25%" />
              <col span="1" style="width: 10%" />
              <col span="1" style="width: 10%" />
              <col span="1" style="width: 20%" />
            </colgroup>
            <thead>
              <tr>
                <th class="text-left font-weight-bold">Run Name</th>
                <th class="text-left font-weight-bold">Run Ticket</th>
                <th class="text-left font-weight-bold">Task Tickets</th>
                <th class="text-center font-weight-bold">XAI Task Status</th>
                <th class="text-center font-weight-bold">Eval Task Status</th>
                <th class="text-left font-weight-bold"></th>
              </tr>
            </thead>
            <tbody>
              <tr
                class="trHover"
                v-for="item in current_pipeline_run_list"
                :key="item.pipeline_run_ticket"
              >
                <td>{{ item.pipeline_run_name }}</td>
                <td>{{ item.pipeline_run_ticket }}</td>
                <td>
                  <tr>
                    <td style="padding: 0 0.5em 0 0">
                      <v-chip
                        class="font-weight-black"
                        size="x-small"
                        color="success"
                        label
                      >
                        XAI
                      </v-chip>
                    </td>
                    <td>
                      {{ item.xai_task_ticket }}
                    </td>
                  </tr>
                  <tr>
                    <td style="padding: 0 0.5em 0 0">
                      <v-chip
                        class="font-weight-black"
                        size="x-small"
                        color="info"
                        label
                      >
                        Eval
                      </v-chip>
                    </td>
                    <td>
                      {{ item.evaluation_task_ticket }}
                    </td>
                  </tr>
                </td>

                <!-- xai task -->
                <td class="stt">
                  <v-tooltip :text="item.xai_task.task_status">
                    <template v-slot:activator="{ props }">
                      <TransitionGroup name="fade" mode="out-in">
                        <v-progress-circular
                          class="st"
                          v-bind="props"
                          :size="20"
                          color="primary"
                          indeterminate
                          v-if="item.xai_task.task_status === 'running'"
                        ></v-progress-circular>
                        <v-icon
                          v-if="item.xai_task.task_status === 'finished'"
                          v-bind="props"
                          class="st"
                          icon="mdi-check-bold"
                          color="success"
                        ></v-icon>
                        <v-icon
                          v-bind="props"
                          class="st"
                          v-if="item.xai_task.task_status === 'stopped'"
                          icon="mdi-stop-circle"
                          color="grey"
                        ></v-icon>
                        <v-icon
                          v-bind="props"
                          class="st"
                          v-if="item.xai_task.task_status === 'error'"
                          icon="mdi-alert-circle"
                          color="error"
                        ></v-icon>
                        <v-icon
                          v-bind="props"
                          class="st"
                          v-if="item.xai_task.task_status === 'initialized'"
                          icon="mdi-arrow-right-drop-circle"
                          color="blue-grey"
                        ></v-icon>
                      </TransitionGroup>
                    </template>
                  </v-tooltip>
                </td>

                <!-- eval task -->
                <td class="stt">
                  <v-tooltip :text="item.evaluation_task.task_status">
                    <template v-slot:activator="{ props }">
                      <TransitionGroup name="fade" mode="out-in">
                        <v-progress-circular
                          class="st"
                          v-bind="props"
                          :size="20"
                          color="primary"
                          indeterminate
                          v-if="item.evaluation_task.task_status === 'running'"
                        ></v-progress-circular>
                        <v-icon
                          v-if="item.evaluation_task.task_status === 'finished'"
                          v-bind="props"
                          class="st"
                          icon="mdi-check-bold"
                          color="success"
                        ></v-icon>
                        <v-icon
                          v-bind="props"
                          class="st"
                          v-if="item.evaluation_task.task_status === 'stopped'"
                          icon="mdi-stop-circle"
                          color="grey"
                        ></v-icon>
                        <v-icon
                          v-bind="props"
                          class="st"
                          v-if="item.evaluation_task.task_status === 'error'"
                          icon="mdi-alert-circle"
                          color="error"
                        ></v-icon>
                        <v-icon
                          v-bind="props"
                          class="st"
                          v-if="
                            item.evaluation_task.task_status === 'initialized'
                          "
                          icon="mdi-arrow-right-drop-circle"
                          color="blue-grey"
                        ></v-icon>
                      </TransitionGroup>
                    </template>
                  </v-tooltip>
                </td>
                <td style="text-align: right" mode="out-in">
                  <v-btn
                    style="margin-left: 0.5em"
                    color="blue"
                    size="x-small"
                    prepend-icon="mdi-clipboard-minus-outline"
                    @click="openPRSDD(item)"
                    :disabled="
                      !(
                        item.xai_task.task_status === 'finished' ||
                        item.evaluation_task.task_status === 'finished'
                      )
                    "
                    >Result</v-btn
                  >
                  <v-btn
                    style="margin-left: 0.5em"
                    color="warning"
                    size="x-small"
                    prepend-icon="mdi-close"
                    @click="stopARun(item)"
                    :disabled="
                      !(
                        item.xai_task.task_status === 'running' ||
                        item.evaluation_task.task_status === 'running'
                      )
                    "
                    >Stop</v-btn
                  >
                  <v-btn
                    style="margin-left: 0.5em"
                    color="error"
                    size="x-small"
                    prepend-icon="mdi-delete"
                    @click="deleteARun(item)"
                    :disabled="
                      item.xai_task.task_status === 'running' ||
                      item.evaluation_task.task_status === 'running'
                    "
                    >Delete</v-btn
                  >
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- pipeline run result detail  -->
    <v-dialog
      id="pipeline-rs-detail-dialog"
      contained
      v-model="prrsdialog"
      persistent
      style="height: 100%"
    >
      <v-card style="height: 100000px">
        <v-card-title>
          <v-card-actions>
            <span class="text-h5"
              >Run: {{ current_pipeline_run.pipeline_name }} on ticket:
              {{ current_pipeline_run.pipeline_run_ticket }}</span
            >
            <v-spacer></v-spacer>
            <v-btn
              size="small"
              variant="outlined"
              color="red-darken-1"
              @click="closePRSDD"
            >
              Close
            </v-btn>
          </v-card-actions>
        </v-card-title>
        <v-divider></v-divider>
        <v-container style="overflow: scroll">
          <v-card-title>
            <span class="text-h6">XAI Task Result</span>
          </v-card-title>
          <v-card-text>
            <v-expansion-panels>
              <v-expansion-panel
                v-if="
                  xai_task_rs.global.length == 0 &&
                  xai_task_rs.local.length == 0
                "
                title="Show Result"
                text="No Result Yet."
              >
              </v-expansion-panel>
              <v-expansion-panel v-else title="Show Result">
                <v-expansion-panel-text>
                  <div v-if="xai_task_rs['global'].length > 0">
                    <v-card-title>
                      <span class="text-h6">Global Explaination</span>
                    </v-card-title>
                    <v-card-text>
                      <v-expansion-panels variant="popout">
                        <v-expansion-panel
                          v-for="item in xai_task_rs['global']"
                          :key="item.file_name"
                        >
                          <v-expansion-panel-title v-slot="{}">
                            {{ item.file_name }}
                          </v-expansion-panel-title>

                          <v-expansion-panel-text
                            v-if="item.file_type === 'img'"
                            class="unselectable"
                            style="overflow-x: auto; text-align: center"
                          >
                            <img
                              :src="item.address"
                              style="max-height: 500px"
                            />
                          </v-expansion-panel-text>
                          <v-expansion-panel-text
                            v-else
                            style="text-align: center"
                          >
                            <a :href="item.address"> Download</a>
                          </v-expansion-panel-text>
                        </v-expansion-panel>
                      </v-expansion-panels>
                    </v-card-text>
                  </div>
                  <v-divider></v-divider>
                  <div v-if="xai_task_rs['local'].length > 0">
                    <v-card-title>
                      <span class="text-h6">Local Explaination</span>
                    </v-card-title>
                    <v-card-text>
                      <v-expansion-panels variant="popout">
                        <v-expansion-panel
                          v-for="sample in xai_task_rs['local']"
                          :key="sample.sample_name"
                        >
                          <v-expansion-panel-title v-slot="{}">
                            {{ sample.sample_name }}
                          </v-expansion-panel-title>
                          <v-expansion-panel-text>
                            <v-expansion-panels variant="popout">
                              <v-expansion-panel
                                v-for="item in sample.explanation_results"
                                :key="item.file_name"
                              >
                                <v-expansion-panel-title v-slot="{}">
                                  {{ item.file_name }}
                                </v-expansion-panel-title>
                                <v-expansion-panel-text
                                  v-if="item.file_type === 'img'"
                                  class="unselectable"
                                  style="overflow-x: auto; text-align: center"
                                >
                                  <img
                                    :src="item.address"
                                    style="max-height: 500px"
                                  />
                                </v-expansion-panel-text>
                                <v-expansion-panel-text
                                  v-else
                                  style="text-align: center"
                                >
                                  This file is not support for present.
                                </v-expansion-panel-text>
                              </v-expansion-panel>
                            </v-expansion-panels>
                          </v-expansion-panel-text>
                        </v-expansion-panel>
                      </v-expansion-panels>
                    </v-card-text>
                  </div>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
          </v-card-text>
          <v-divider></v-divider>

          <!-- evaluation task result -->
          <v-card-title>
            <span class="text-h6">Evaluation Task Result</span>
          </v-card-title>
          <v-card-text>
            <v-expansion-panels>
              <v-expansion-panel
                v-if="
                  evaluation_task_rs.global.length == 0 &&
                  evaluation_task_rs.local.length == 0
                "
                title="Show Result"
                text="No Result Yet."
              >
              </v-expansion-panel>
              <v-expansion-panel v-else title="Show Result">
                <v-expansion-panel-text>
                  <div v-if="evaluation_task_rs['global'].length > 0">
                    <v-card-title>
                      <span class="text-h6"
                        >Global Explaination Evaluation</span
                      >
                    </v-card-title>
                    <v-card-text>
                      <v-expansion-panels variant="popout">
                        <v-expansion-panel
                          v-for="item in evaluation_task_rs['global']"
                          :key="item.file_name"
                        >
                          <v-expansion-panel-title v-slot="{}">
                            {{ item.file_name }}
                          </v-expansion-panel-title>

                          <v-expansion-panel-text
                            v-if="item.file_type === 'img'"
                            class="unselectable"
                            style="overflow-x: auto; text-align: center"
                          >
                            <img :src="item.address" />
                          </v-expansion-panel-text>
                          <v-expansion-panel-text
                            style="text-align: center"
                            v-else
                          >
                            <a :href="item.address"> Download</a>
                          </v-expansion-panel-text>
                        </v-expansion-panel>
                      </v-expansion-panels>
                    </v-card-text>
                  </div>
                  <v-divider></v-divider>
                  <div v-if="evaluation_task_rs['local'].length > 0">
                    <v-card-title>
                      <span class="text-h6">Local Explaination Evaluation</span>
                    </v-card-title>
                    <v-card-text>
                      <v-expansion-panels variant="popout">
                        <v-expansion-panel
                          v-for="sample in evaluation_task_rs['local']"
                          :key="sample.sample_name"
                        >
                          <v-expansion-panel-title v-slot="{}">
                            {{ sample.sample_name }}
                          </v-expansion-panel-title>
                          <v-expansion-panel-text>
                            <v-expansion-panels variant="popout">
                              <v-expansion-panel
                                v-for="item in sample.explanation_results"
                                :key="item.file_name"
                              >
                                <v-expansion-panel-title v-slot="{}">
                                  {{ item.file_name }}
                                </v-expansion-panel-title>
                                <v-expansion-panel-text
                                  v-if="item.file_type === 'img'"
                                  class="unselectable"
                                  style="overflow-x: auto; text-align: center"
                                >
                                  <img :src="item.address" />
                                </v-expansion-panel-text>
                                <v-expansion-panel-text
                                  v-else
                                  style="text-align: center"
                                >
                                  This file is not support for present.
                                </v-expansion-panel-text>
                              </v-expansion-panel>
                            </v-expansion-panels>
                          </v-expansion-panel-text>
                        </v-expansion-panel>
                      </v-expansion-panels>
                    </v-card-text>
                  </div>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
          </v-card-text>
        </v-container>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
const typeMap = {
  db: "Database",
  xai: "XAI",
  model: "AI Model",
  evaluation: "Evaluation",
  Database: "db",
  XAI: "xai",
  "AI Model": "model",
  Evaluation: "evaluation",
};

export default {
  data: () => ({
    valid: false,
    pipelines: [],
    disabled: false,
    dialog: false,
    prldialog: false,
    prrsdialog: false,
    current_pipeline: {
      pipeline_name: "",
      xai_task_sheet_id: "",
      evaluation_task_sheet_id: "",
    },
    xaiTaskSheetList: [],
    evalTaskSheetList: [],
    current_pipeline_run_list: [],
    current_pipeline_run: {},
    xai_task_rs: {
      global: [],
      local: [],
    },
    evaluation_task_rs: {
      global: [],
      local: [],
    },
    fetchPipelineRunInv: undefined,
  }),
  mounted: function () {
    this.fetchPipeline();
  },
  methods: {
    fetchTaskResult(task_ticket, task_type) {
      this.trdialog = true;
      this.ax.get(
        "http://127.0.0.1:5006/task_publisher/task_result",
        {
          task_ticket,
        },
        {
          success: (response) => {
            console.log(response.data);
            let localRs = [];
            for (const [key, value] of Object.entries(response.data["local"])) {
              localRs.push({
                sample_name: key,
                explanation_results: value,
              });
            }
            if (task_type === "xai") {
              this.xai_task_rs["local"] = localRs;
            } else {
              this.evaluation_task_rs["local"] = localRs;
            }

            let globalRs = [];
            for (const i of response.data["global"]) {
              globalRs.push(i);
            }
            if (task_type === "xai") {
              this.xai_task_rs["global"] = globalRs;
            } else {
              this.evaluation_task_rs["global"] = globalRs;
            }
          },
          error: () => {},
          final: () => {},
        }
      );
    },
    currentPipelineRunnable() {
      return (
        this.current_pipeline.xai_task_status === "initialized" ||
        this.current_pipeline.evaluation_task_status === "initialized"
      );
    },
    showSheetListForPipeline(id, list) {
      if (id === "") {
        return list;
      }

      let rs = [];
      for (const sheet of list) {
        if (sheet.task_sheet_id === id) {
          rs.push(sheet);
        }
      }
      if (rs.length > 0) {
        if (rs[0].task_type === "xai") {
          this.current_xai_task_sheet_id = id;
        }
        if (rs[0].task_type === "evaluation") {
          this.current_evaluation_task_sheet_id = id;
        }
      }
      return rs;
    },
    openPRSDD(item) {
      this.prrsdialog = true;
      this.current_pipeline_run = item;
      this.fetchTaskResult(item.xai_task_ticket, "xai");
      this.fetchTaskResult(item.evaluation_task_ticket, "evaluation");
    },
    closePRSDD() {
      this.prrsdialog = false;
      setTimeout(() => {
        this.current_pipeline_run = {};
      }, 500);
    },
    stopARun(item) {
      const pipeline_run_ticket = item.pipeline_run_ticket;
      this.ax.post(
        "http://127.0.0.1:5006/task_publisher/pipeline_run",
        {
          act: "stop",
          pipeline_run_ticket,
        },
        {
          success: (response) => {
            this.fetchPipelineRuntList();
          },
          error: () => {},
          final: () => {},
        }
      );
    },
    deleteARun(item) {
      const pipeline_run_ticket = item.pipeline_run_ticket;
      this.ax.post(
        "http://127.0.0.1:5006/task_publisher/pipeline_run",
        {
          act: "delete",
          pipeline_run_ticket,
        },
        {
          success: (response) => {
            this.fetchPipelineRuntList();
          },
          error: () => {},
          final: () => {},
        }
      );
    },
    runCurrentPipeline() {
      console.log("run pipeline " + this.current_pipeline.pipeline_id);
      this.ax.post(
        "http://127.0.0.1:5006/task_publisher/pipeline",
        {
          act: "run",
          pipeline_id: this.current_pipeline.pipeline_id,
        },
        {
          success: (response) => {
            this.fetchPipelineRuntList();
          },
          error: () => {},
          final: () => {},
        }
      );
    },
    getTaskStatus(item) {
      return item.start_time !== undefined && item.task_status === "initialized"
        ? "stopped"
        : item.task_status;
    },

    openPRLD(item) {
      this.prldialog = true;
      this.current_pipeline = item;
      this.fetchPipelineRuntList();
    },
    closePRLD() {
      this.prldialog = false;
      clearInterval(this.fetchPipelineRunInv);
      setTimeout(() => {
        this.current_pipeline = {
          pipeline_name: "",
          xai_task_sheet_id: "",
          evaluation_task_sheet_id: "",
        };
      }, 500);
    },
    resetForm() {
      setTimeout(() => {
        this.current_pipeline = {
          pipeline_name: "",
          xai_task_sheet_id: "",
          evaluation_task_sheet_id: "",
        };
        this.xaiTaskSheetList = [];
        this.evalTaskSheetList = [];
        this.disabled = false;
      }, 300);
    },
    openD(item) {
      if (item != undefined) {
        this.disabled = true;
        this.current_pipeline = item;
      } else {
        this.fetchTaskSheetList();
        this.disabled = false;
      }
      this.dialog = true;
    },
    closeD() {
      this.resetForm();
      this.dialog = false;
    },
    fetchPipelineRuntList() {
      console.log("fetch pipeline run list");
      const pipeline_id = this.current_pipeline.pipeline_id;
      this.ax.get(
        "http://127.0.0.1:5006/task_publisher/pipeline_run",
        {
          pipeline_id,
        },
        {
          success: (response) => {
            // console.log(response.data);
            this.current_pipeline_run_list = response.data;
          },
          error: () => {},
          final: () => {
            let hasRunning = false;
            for (const pipeline_run of this.current_pipeline_run_list) {
              if (
                pipeline_run.xai_task.task_status === "running" ||
                pipeline_run.evaluation_task.task_status === "running"
              ) {
                hasRunning = true;
                break;
              }
            }

            clearInterval(this.fetchPipelineRunInv);
            if (hasRunning) {
              this.fetchPipelineRunInv = setInterval(() => {
                this.fetchPipelineRuntList();
              }, 10000);
            }
          },
        }
      );
    },
    fetchTaskSheetList() {
      console.log("fetch task sheet list");
      this.ax.get(
        "http://127.0.0.1:5006/task_publisher/task_sheet",
        {},
        {
          success: (response) => {
            let xaiTaskSheetList = [];
            let evalTaskSheetList = [];
            for (const sheet of response.data) {
              if (sheet.task_type === "xai") {
                xaiTaskSheetList.push(sheet);
              }
              if (sheet.task_type === "evaluation") {
                evalTaskSheetList.push(sheet);
              }
            }
            this.xaiTaskSheetList = xaiTaskSheetList;
            this.evalTaskSheetList = evalTaskSheetList;
          },
          error: () => {},
          final: () => {},
        }
      );
    },
    fetchPipeline(cb) {
      console.log("fetch pipeline");
      this.ax.get(
        "http://127.0.0.1:5006/task_publisher/pipeline",
        {},
        {
          success: (response) => {
            this.pipelines = response.data;
            if (cb !== undefined) {
              cb();
            }
          },
          error: () => {},
          final: () => {},
        }
      );
    },
    deletePipeline(item) {
      this.ax.post(
        "http://127.0.0.1:5006/task_publisher/pipeline",
        {
          act: "delete",
          pipeline_id: item.pipeline_id,
        },
        {
          success: (response) => {
            this.fetchPipeline();
          },
          error: () => {},
          final: () => {},
        }
      );
    },
    async submitAddPipelineAction(e) {
      // this.validate();
      e.preventDefault();
      const { valid } = await this.$refs.form.validate();
      const pipeline_name = this.current_pipeline.pipeline_name;
      const xai_task_sheet_id = this.current_pipeline.xai_task_sheet_id;
      const evaluation_task_sheet_id =
        this.current_pipeline.evaluation_task_sheet_id;

      if (valid) {
        this.ax.post(
          "http://127.0.0.1:5006/task_publisher/pipeline",
          {
            act: "create",
            pipeline_name,
            xai_task_sheet_id,
            evaluation_task_sheet_id,
          },
          {
            success: (response) => {
              console.log(response.data);
            },
            error: () => {},
            final: () => {
              this.fetchPipeline();
              this.closeD();
            },
          }
        );
      }
    },
  },
};
</script>

<style>
.fade-enter-active {
  transition: all 0.5s ease-in;
}
.fade-leave-active {
  transition: all 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
.stt {
  position: relative;
}
.st {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
}
</style>
