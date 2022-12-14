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
          <v-btn size="small" color="success" @click="openD">
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
        <col span="1" style="width: 15%" />
        <col span="1" style="width: 30%" />
        <col span="1" style="width: 35%" />
      </colgroup>
      <thead>
        <tr>
          <th class="text-left font-weight-bold">ID</th>
          <th class="text-left font-weight-bold">Name</th>
          <th class="text-left font-weight-bold">Status (XAI, Evaluation)</th>
          <th class="text-left font-weight-bold"></th>
        </tr>
      </thead>
      <tbody>
        <tr class="trHover" v-for="item in pipelines" :key="item.pipeline_id">
          <td>{{ item.pipeline_id }}</td>
          <td>{{ item.pipeline_name }}</td>
          <td>
            {{
              item.xai_task_sheet_status +
              ", " +
              item.evaluation_task_sheet_status
            }}
          </td>
          <td style="text-align: right">
            <v-btn
              color="primary"
              size="x-small"
              prepend-icon="mdi-television"
              @click="openPDD(item)"
              >Detials</v-btn
            >
            <v-btn
              style="margin-left: 0.5em"
              color="success"
              size="x-small"
              prepend-icon="mdi-play"
              @click="openPRSDD(item)"
              >Tasks</v-btn
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
                  v-model="pipeline_name"
                  :rules="[(v) => !!v || 'Name is required']"
                  required
                ></v-text-field>
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

    <!-- pipeline detail  -->
    <v-dialog
      id="pipeline-detail-dialog"
      contained
      v-model="pddialog"
      max-width="600px"
      persistent
    >
      <v-form id="pipeline-detail-form" ref="form2">
        <v-card>
          <v-card-title>
            <span class="text-h5">Pipeline Detail</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-text-field
                  label="Pipeline Name*"
                  name="pipeline_name"
                  v-model="current_pipeline.pipeline_name"
                  readonly
                ></v-text-field>
              </v-row>

              <!-- xai -->
              <v-row>
                <v-select
                  label="XAI Task Sheet Name"
                  :items="
                    showSheetListForPipeline(
                      current_pipeline.xai_task_sheet_id,
                      xaiTaskSheetList
                    )
                  "
                  item-title="task_sheet_name"
                  item-value="task_sheet_id"
                  name="current_xai_task_sheet_id"
                  v-model="current_xai_task_sheet_id"
                  :rules="[(v) => !!v || 'This field is required']"
                  ref="current_xai_task_sheet_id"
                  :readonly="current_xai_task_sheet_id !== ''"
                  hide-details
                ></v-select>
              </v-row>
              <v-row
                class="mt-8"
                v-if="current_pipeline.xai_task_ticket === ''"
              >
                <v-text-field
                  ref="current_xai_task_name"
                  label="XAI Task Name*"
                  name="current_xai_task_name"
                  v-model="current_xai_task_name"
                  :rules="[(v) => !!v || 'This field is required']"
                  hide-details
                ></v-text-field>
                <div class="ml-3" style="margin: auto; bottom: 0; top: 0">
                  <v-btn color="success" @click="addXAITaskSheetSheet"
                    >ADD</v-btn
                  >
                </div>
              </v-row>

              <v-row
                class="mt-8"
                v-if="current_pipeline.xai_task_ticket !== ''"
              >
                <v-text-field
                  label="XAI Task Ticket"
                  name="current_xai_task_ticket"
                  v-model="current_pipeline.xai_task_ticket"
                  hide-details
                  readonly
                ></v-text-field>
              </v-row>

              <!-- eval -->
              <v-row class="mt-8">
                <v-select
                  label="Evaluation Task Sheet Name"
                  :items="
                    showSheetListForPipeline(
                      current_pipeline.evaluation_task_sheet_id,
                      evalTaskSheetList
                    )
                  "
                  item-title="task_sheet_name"
                  item-value="task_sheet_id"
                  name="current_evaluation_task_sheet_id"
                  v-model="current_evaluation_task_sheet_id"
                  :rules="[(v) => !!v || 'This field is required']"
                  ref="current_evaluation_task_sheet_id"
                  :readonly="current_evaluation_task_sheet_id !== ''"
                  hide-details
                ></v-select>
              </v-row>
              <v-row
                class="mt-9"
                v-if="current_pipeline.evaluation_task_ticket === ''"
              >
                <v-text-field
                  ref="current_evaluation_task_name"
                  label="Evaluation Task Name*"
                  name="current_evaluation_task_name"
                  v-model="current_evaluation_task_name"
                  :rules="[(v) => !!v || 'This field is required']"
                  hide-details
                ></v-text-field>
                <div class="ml-3" style="margin: auto; bottom: 0; top: 0">
                  <v-btn color="success" @click="addEvaluationTaskSheet"
                    >ADD</v-btn
                  >
                </div>
              </v-row>

              <v-row
                class="mt-8"
                v-if="current_pipeline.evaluation_task_ticket !== ''"
              >
                <v-text-field
                  label="Evaluation Task Ticket"
                  name="current_evaluation_task_ticket"
                  v-model="current_pipeline.evaluation_task_ticket"
                  hide-details
                  readonly
                ></v-text-field>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="red-darken-1" @click="closePDD"> Close </v-btn>
          </v-card-actions>
        </v-card>
      </v-form>
    </v-dialog>

    <!-- pipeline result detail  -->
    <v-dialog
      id="pipeline-rs-detail-dialog"
      contained
      v-model="prsddialog"
      persistent
    >
      <v-form id="pipeline-rs-detail-form" ref="form2">
        <v-card>
          <v-card-title>
            <v-card-actions>
              <span class="text-h5">Pipeline Result Detail</span>
              <v-spacer></v-spacer>
              <v-btn
                size="small"
                variant="outlined"
                color="success"
                @click="runPipeline"
                :disabled="!currentPipelineRunnable()"
                >RUN</v-btn
              >
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
          <v-container style="overflow: scroll; max-height: 700px">
            <v-card-title>
              <span class="text-h6">XAI Task Result</span>
            </v-card-title>
            <v-card-text>
              <v-container>
                <v-expansion-panels>
                  <v-expansion-panel
                    v-if="current_pipeline.xai_task_sheet_status !== 'finished'"
                    title="Show Result"
                    text="No Result Yet."
                  >
                  </v-expansion-panel>
                  <v-expansion-panel
                    v-if="current_pipeline.xai_task_sheet_status === 'finished'"
                    title="Show Result"
                  >
                    <v-expansion-panel-text
                      style="overflow: scroll; max-height: 500px"
                    >
                      <v-card-title>
                        <span class="text-h6">Global Explaination</span>
                      </v-card-title>
                      <v-card-text>
                        <v-table>
                          <colgroup>
                            <col span="1" style="width: 30%" />
                            <col span="1" style="width: 70%" />
                          </colgroup>
                          <thead>
                            <tr>
                              <th class="text-left font-weight-bold">
                                File Name
                              </th>
                              <th class="text-left font-weight-bold">
                                Content
                              </th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr
                              class="trHover"
                              v-for="item in xai_task_rs['global']"
                              :key="item.filename"
                            >
                              <td>{{ item.file_name }}</td>
                              <td>
                                <img :src="item.address" alt="" srcset="" />
                              </td>
                            </tr>
                          </tbody>
                        </v-table>
                      </v-card-text>

                      <v-divider></v-divider>
                      <v-card-title>
                        <span class="text-h6">Local Explaination</span>
                      </v-card-title>
                      <v-card-text>
                        <v-table>
                          <colgroup>
                            <col span="1" style="width: 30%" />
                            <col span="1" style="width: 70%" />
                          </colgroup>
                          <thead>
                            <tr>
                              <th class="text-left font-weight-bold">
                                File Name
                              </th>
                              <th class="text-left font-weight-bold">
                                Content
                              </th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr
                              class="trHover"
                              v-for="item in xai_task_rs['local']"
                              :key="item.filename"
                            >
                              <td>{{ item.file_name }}</td>
                              <td>
                                <img :src="item.address" alt="" srcset="" />
                              </td>
                            </tr>
                          </tbody>
                        </v-table>
                      </v-card-text>
                    </v-expansion-panel-text>
                  </v-expansion-panel>
                </v-expansion-panels>
              </v-container>
            </v-card-text>
            <v-divider></v-divider>
            <v-card-title>
              <span class="text-h6">Evaluation Task Result</span>
            </v-card-title>
            <v-card-text>
              <v-container>
                <v-expansion-panels>
                  <v-expansion-panel
                    v-if="
                      current_pipeline.evaluation_task_sheet_status !==
                      'finished'
                    "
                    title="Show Result"
                    text="No Result Yet."
                  >
                  </v-expansion-panel>
                  <v-expansion-panel
                    v-if="
                      current_pipeline.evaluation_task_sheet_status ===
                      'finished'
                    "
                    title="Show Result"
                  >
                    <v-expansion-panel-text
                      style="overflow: scroll; max-height: 500px"
                    >
                      <v-card-title>
                        <span class="text-h6">Global Explaination</span>
                      </v-card-title>
                      <v-card-text>
                        <v-table>
                          <colgroup>
                            <col span="1" style="width: 30%" />
                            <col span="1" style="width: 70%" />
                          </colgroup>
                          <thead>
                            <tr>
                              <th class="text-left font-weight-bold">
                                File Name
                              </th>
                              <th class="text-left font-weight-bold">
                                Content
                              </th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr
                              class="trHover"
                              v-for="item in evaluation_task_rs['global']"
                              :key="item.filename"
                            >
                              <td>{{ item.file_name }}</td>
                              <td>
                                <img :src="item.address" alt="" srcset="" />
                              </td>
                            </tr>
                          </tbody>
                        </v-table>
                      </v-card-text>

                      <v-divider></v-divider>
                      <v-card-title>
                        <span class="text-h6">Local Explaination</span>
                      </v-card-title>
                      <v-card-text>
                        <v-table>
                          <colgroup>
                            <col span="1" style="width: 30%" />
                            <col span="1" style="width: 70%" />
                          </colgroup>
                          <thead>
                            <tr>
                              <th class="text-left font-weight-bold">
                                File Name
                              </th>
                              <th class="text-left font-weight-bold">
                                Content
                              </th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr
                              class="trHover"
                              v-for="item in evaluation_task_rs['local']"
                              :key="item.filename"
                            >
                              <td>{{ item.file_name }}</td>
                              <td>
                                <img :src="item.address" alt="" srcset="" />
                              </td>
                            </tr>
                          </tbody>
                        </v-table>
                      </v-card-text>
                    </v-expansion-panel-text>
                  </v-expansion-panel>
                </v-expansion-panels>
              </v-container>
            </v-card-text>
          </v-container>
        </v-card>
      </v-form>
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
    pddialog: false,
    prsddialog: false,
    pipeline_name: "",
    current_pipeline: "",
    xaiTaskSheetList: [],
    evalTaskSheetList: [],
    current_xai_task_sheet_id: "",
    current_evaluation_task_sheet_id: "",
    current_xai_task_name: "",
    current_evaluation_task_name: "",
    xai_task_rs: {
      global: [],
      local: [],
    },
    evaluation_task_rs: {
      global: [],
      local: [],
    },
    fetchPipelineInv: undefined,
  }),
  mounted: function () {
    this.fetchPipeline();
  },
  methods: {
    fetchTaskResult(task_ticket, task_type) {
      this.trdialog = true;
      // console.log(item);
      this.ax.get(
        "http://127.0.0.1:5006/task_publisher/task_result",
        {
          task_ticket,
        },
        {
          success: (response) => {
            let localRs = [];
            for (const i of response.data["local"]) {
              if (i.file_type === "img") {
                localRs.push(i);
              }
            }
            localRs.sort();
            if (task_type === "xai") {
              this.xai_task_rs["local"] = localRs;
            } else {
              this.evaluation_task_rs["local"] = localRs;
            }

            let globalRs = [];
            for (const i of response.data["global"]) {
              if (i.file_type === "img") {
                globalRs.push(i);
              }
            }
            globalRs.sort();
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
        this.current_pipeline.xai_task_sheet_status === "initialized" ||
        this.current_pipeline.evaluation_task_sheet_status === "initialized"
      );
    },
    runPipeline() {
      this.ax.post(
        "http://127.0.0.1:5006/task_publisher/pipeline",
        {
          act: "run",
          pipeline_id: this.current_pipeline.pipeline_id,
        },
        {
          success: (response) => {
            console.log(response.data);
          },
          error: () => {},
          final: () => {
            this.fetchPipeline();
            this.closePRSDD();
          },
        }
      );
    },
    addEvaluationTaskSheet() {
      console.log(this.current_pipeline);
      this.$refs.current_evaluation_task_sheet_id.validate().then((v) => {
        if (v[0] === undefined) {
          console.log(this.current_evaluation_task_sheet_id);
          this.$refs.current_evaluation_task_name.validate().then((v) => {
            if (v[0] === undefined) {
              console.log(this.current_evaluation_task_name);
              // valid
              this.ax.post(
                "http://127.0.0.1:5006/task_publisher/pipeline",
                {
                  act: "add_task",
                  pipeline_id: this.current_pipeline.pipeline_id,
                  task_name: this.current_evaluation_task_name,
                  task_sheet_id: this.current_evaluation_task_sheet_id,
                },
                {
                  success: (response) => {
                    console.log(response.data);
                  },
                  error: () => {},
                  final: () => {
                    this.fetchPipeline(() => {
                      for (const p of this.pipelines) {
                        if (
                          p.pipeline_id === this.current_pipeline.pipeline_id
                        ) {
                          this.current_pipeline = p;
                        }
                      }
                    });
                    // this.closeTaskDialog();
                  },
                }
              );
            }
          });
        }
      });
    },
    addXAITaskSheetSheet() {
      console.log(this.current_pipeline);
      this.$refs.current_xai_task_sheet_id.validate().then((v) => {
        if (v[0] === undefined) {
          console.log(this.current_xai_task_sheet_id);
          this.$refs.current_xai_task_name.validate().then((v) => {
            if (v[0] === undefined) {
              console.log(this.current_xai_task_name);
              // valid
              this.ax.post(
                "http://127.0.0.1:5006/task_publisher/pipeline",
                {
                  act: "add_task",
                  pipeline_id: this.current_pipeline.pipeline_id,
                  task_name: this.current_xai_task_name,
                  task_sheet_id: this.current_xai_task_sheet_id,
                },
                {
                  success: (response) => {
                    console.log(response.data);
                    this.fetchTaskSheetList();
                  },
                  error: () => {},
                  final: () => {
                    this.fetchPipeline(() => {
                      for (const p of this.pipelines) {
                        if (
                          p.pipeline_id === this.current_pipeline.pipeline_id
                        ) {
                          this.current_pipeline = p;
                        }
                      }
                    });

                    // this.closeTaskDialog();
                  },
                }
              );
            }
          });
        }
      });
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
      this.prsddialog = true;
      this.current_pipeline = item;
      if (this.current_pipeline.xai_task_sheet_status === "finished") {
        this.fetchTaskResult(this.current_pipeline.xai_task_ticket, "xai");
      }
      if (this.current_pipeline.evaluation_task_sheet_status === "finished") {
        this.fetchTaskResult(
          this.current_pipeline.evaluation_task_ticket,
          "evaluation"
        );
      }
    },
    closePRSDD() {
      this.prsddialog = false;
      this.current_pipeline = {};
    },
    openPDD(item) {
      this.fetchTaskSheetList();
      this.pddialog = true;
      this.current_pipeline = item;
    },
    closePDD() {
      this.pddialog = false;
      this.current_pipeline = {};
      this.current_xai_task_name = "";
      this.current_xai_task_sheet_id = "";
      this.current_evaluation_task_name = "";
      this.current_evaluation_task_sheet_id = "";
    },
    resetForm() {
      this.pipeline_name = "";
    },
    openD() {
      this.resetForm();
      this.disabled = false;
      this.dialog = true;
    },
    closeD() {
      this.dialog = false;
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
      console.log("fetch task sheet list");
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
          final: () => {
            let hasRunning = false;
            for (const p of this.pipelines) {
              if (
                p.xai_task_sheet_status === "running" ||
                p.evaluation_task_sheet_status === "running"
              ) {
                hasRunning = true;
                break;
              }
            }
            clearInterval(this.fetchPipelineInv);
            if (hasRunning) {
              this.fetchPipelineInv = setInterval(() => {
                this.fetchPipeline();
              }, 2000);
            }
          },
        }
      );
    },
    deletePipeline(item) {
      this.ax.post(
        "http://127.0.0.1:5006/task_publisher/pipeline",
        {
          act: "del",
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
      const pipeline_name = this.pipeline_name;

      if (valid) {
        this.ax.post(
          "http://127.0.0.1:5006/task_publisher/pipeline",
          {
            act: "create",
            pipeline_name,
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

<style></style>
