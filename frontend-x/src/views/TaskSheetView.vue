<template>
  <v-card class="mx-auto" style="height: 100%" :elevation="3">
    <template v-slot:title>
      <div class="clearfix">
        <div style="width: 50%; float: left; padding: 0.1em">
          Created TaskSheet
        </div>
        <div
          style="width: 50%; float: right; text-align: right; padding: 0.1em"
        >
          <v-btn size="small" color="success" @click="openD">
            Add Task Sheet
          </v-btn>
        </div>
      </div>
    </template>

    <v-divider></v-divider>
    <!-- <v-card-text> This is content </v-card-text> -->
    <v-table>
      <colgroup>
        <col span="1" style="width: 20%" />
        <col span="1" style="width: 25%" />
        <col span="1" style="width: 10%" />
        <col span="1" style="width: 45%" />
      </colgroup>
      <thead>
        <tr>
          <th class="text-left font-weight-bold">ID</th>
          <th class="text-left font-weight-bold">Name</th>
          <th class="text-left font-weight-bold">Task Type</th>
          <th class="text-left font-weight-bold"></th>
        </tr>
      </thead>
      <tbody>
        <tr class="trHover" v-for="item in sheets" :key="item.name">
          <td>{{ item.task_sheet_id }}</td>
          <td>{{ item.task_sheet_name }}</td>
          <td>{{ typeMap[item.task_type] }}</td>
          <td style="text-align: right">
            <v-btn
              color="blue"
              size="x-small"
              prepend-icon="mdi-television"
              @click="showTaskSheetDetail(item)"
              >Detials</v-btn
            >
            <v-btn
              style="margin-left: 0.5em"
              color="success"
              size="x-small"
              prepend-icon="mdi-play"
              @click="showTaskDialog(item)"
              >Tasks</v-btn
            >
            <v-btn
              style="margin-left: 0.5em"
              color="error"
              size="x-small"
              prepend-icon="mdi-delete"
              @click="deleteTaskSheet(item)"
              >Delete</v-btn
            >
          </td>
        </tr>
      </tbody>
    </v-table>

    <!-- create task sheet -->
    <v-dialog
      id="task-sheet-create-dialog"
      contained
      v-model="dialog"
      max-width="600px"
      style="height: 100%"
      persistent
    >
      <v-card>
        <v-form
          id="task-sheet-create-form"
          ref="form"
          v-model="valid"
          lazy-validation
          @submit="submitAction"
          :disabled="disabled"
        >
          <v-card-title>
            <span v-if="!disabled" class="text-h5">New Task Sheet</span>
            <span v-if="disabled" class="text-h5">Task Sheet Detail</span>
          </v-card-title>
          <v-card-text style="overflow: scroll; max-height: 700px">
            <v-container>
              <v-row>
                <v-text-field
                  label="Task Sheet Name*"
                  name="task_sheet_name"
                  v-model="task_sheet_name"
                  :rules="[(v) => !!v || 'Name is required']"
                  required
                  density="compact"
                ></v-text-field>
              </v-row>
              <v-row>
                <v-select
                  label="Task Type*"
                  :items="['XAI', 'Evaluation']"
                  :rules="[(v) => !!v || 'Task type is required']"
                  name="task_type"
                  v-model="task_type"
                  required
                  density="compact"
                ></v-select>
              </v-row>
              <v-row>
                <v-select
                  label="DB Service*"
                  :items="dbSrviceList"
                  item-title="executor_endpoint_url"
                  item-value="executor_id"
                  :rules="[(v) => !!v || 'Task type is required']"
                  name="db_service_executor_id"
                  v-model="db_service_executor_id"
                  required
                  density="compact"
                ></v-select>
              </v-row>
              <v-row>
                <v-select
                  label="Model Service*"
                  :items="modelSrviceList"
                  item-title="executor_endpoint_url"
                  item-value="executor_id"
                  :rules="[(v) => !!v || 'Task type is required']"
                  name="model_service_executor_id"
                  v-model="model_service_executor_id"
                  required
                  density="compact"
                ></v-select>
              </v-row>
              <v-row>
                <v-select
                  label="XAI Service*"
                  :items="xaiSrviceList"
                  item-title="executor_endpoint_url"
                  item-value="executor_id"
                  :rules="[(v) => !!v || 'Task type is required']"
                  name="xai_service_executor_id"
                  v-model="xai_service_executor_id"
                  required
                  density="compact"
                ></v-select>
              </v-row>
              <v-row>
                <v-select
                  label="Evaluation Service*"
                  :items="evaluationSrviceList"
                  item-title="executor_endpoint_url"
                  item-value="executor_id"
                  :rules="[(v) => !!v || 'Task type is required']"
                  name="evaluation_service_executor_id"
                  v-model="evaluation_service_executor_id"
                  required
                  density="compact"
                ></v-select>
              </v-row>
              <!-- <v-row v-if="task_type === 'Evaluation'">
                <v-text-field
                  label="Explanation Task Ticket*"
                  name="explanation_task_ticket"
                  v-model="explanation_task_ticket"
                  :rules="[(v) => !!v || 'Explanation task ticket is required']"
                  required
                ></v-text-field>
              </v-row> -->
              <v-row>
                <v-textarea
                  name="task_parameters"
                  v-model="task_parameters"
                  label="Task Parameters"
                  :rules="infoRules"
                  density="compact"
                ></v-textarea>
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
              form="task-sheet-create-form"
            >
              Submit
            </v-btn>
          </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>

    <!-- task list -->
    <v-dialog
      id="task-list-dialog"
      style="height: 100%"
      contained
      v-model="tldialog"
    >
      <v-card style="height: 100000px">
        <v-card-title>
          <v-card-actions>
            <span class="text-h5">Task List</span>

            <v-spacer></v-spacer>

            <v-btn
              size="small"
              variant="outlined"
              color="green-darken-1"
              form="task-sheet-create-form"
              @click="runTaskFromTaskSheet"
            >
              Run
            </v-btn>
            <v-btn
              size="small"
              variant="outlined"
              color="red-darken-1"
              @click="closeTaskDialog"
            >
              Close
            </v-btn>
          </v-card-actions>
        </v-card-title>
        <v-divider></v-divider>
        <v-divider></v-divider>

        <v-card-text>
          <v-table>
            <colgroup>
              <col span="1" style="width: 10%" />
              <col span="1" style="width: 30%" />
              <col span="1" style="width: 15%" />
              <col span="1" style="width: 15%" />
              <col span="1" style="width: 10%" />
              <col span="1" style="width: 20%" />
            </colgroup>
            <thead>
              <tr>
                <th class="text-left font-weight-bold">Task Name</th>
                <th class="text-left font-weight-bold">Task Ticket</th>
                <th class="text-left font-weight-bold">Start Time</th>
                <th class="text-left font-weight-bold">End Time</th>
                <th class="text-center font-weight-bold">Status</th>
                <th class="text-left font-weight-bold"></th>
              </tr>
            </thead>
            <tbody>
              <tr class="trHover" v-for="item in tasks" :key="item.task_ticket">
                <td>{{ item.task_name }}</td>
                <td>{{ item.task_ticket }}</td>
                <td>{{ timestampFormat(item.start_time) }}</td>
                <td>{{ timestampFormat(item.end_time) }}</td>
                <td class="stt">
                  <v-tooltip :text="item.task_status">
                    <template v-slot:activator="{ props }">
                      <TransitionGroup name="fade" mode="out-in">
                        <v-progress-circular
                          class="st"
                          v-bind="props"
                          :size="20"
                          color="primary"
                          indeterminate
                          v-if="item.task_status === 'running'"
                        ></v-progress-circular>
                        <v-icon
                          v-if="item.task_status === 'finished'"
                          v-bind="props"
                          class="st"
                          icon="mdi-check-bold"
                          color="success"
                        ></v-icon>
                        <v-icon
                          v-bind="props"
                          class="st"
                          v-if="item.task_status === 'stopped'"
                          icon="mdi-stop-circle"
                          color="grey"
                        ></v-icon>
                        <v-icon
                          v-bind="props"
                          class="st"
                          v-if="item.task_status === 'error'"
                          icon="mdi-alert-circle"
                          color="error"
                        ></v-icon>
                        <v-icon
                          v-bind="props"
                          class="st"
                          v-if="item.task_status === 'initialized'"
                          icon="mdi-arrow-right-drop-circle"
                          color="blue-grey"
                        ></v-icon>
                      </TransitionGroup>
                    </template>
                  </v-tooltip>
                </td>
                <td style="text-align: right">
                  <v-btn
                    :disabled="item.task_status !== 'finished'"
                    style="margin-left: 0.5em"
                    color="blue"
                    size="x-small"
                    prepend-icon="mdi-clipboard-minus-outline"
                    @click="showTaskResult(item)"
                    >Result</v-btn
                  >
                  <v-btn
                    :disabled="item.task_status !== 'running'"
                    style="margin-left: 0.5em"
                    color="warning"
                    size="x-small"
                    prepend-icon="mdi-close"
                    @click="stopATask(item)"
                    >Stop</v-btn
                  >
                  <v-btn
                    style="margin-left: 0.5em"
                    color="error"
                    size="x-small"
                    prepend-icon="mdi-delete"
                    @click="deleteATask(item)"
                    :disabled="
                      item.pipeline_id !== '' || item.task_status === 'running'
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

    <!-- task result -->
    <v-dialog
      id="task-result-dialog"
      style="height: 100%"
      contained
      v-model="trdialog"
      persistent
    >
      <v-card>
        <v-card-title>
          <v-card-actions>
            <span class="text-h5">Task Result</span>

            <v-spacer></v-spacer>

            <v-btn
              size="small"
              variant="outlined"
              color="red-darken-1"
              @click="closeTaskResultDialog"
            >
              Close
            </v-btn>
          </v-card-actions>
        </v-card-title>
        <v-container style="overflow: scroll">
          <div v-if="task_rs['global'].length > 0">
            <v-card-title>
              <span class="text-h6">Global Explaination</span>
            </v-card-title>
            <v-card-text>
              <v-expansion-panels variant="popout">
                <v-expansion-panel
                  v-for="item in task_rs['global']"
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
                  <v-expansion-panel-text v-else>
                    This file is not support for present.
                  </v-expansion-panel-text>
                </v-expansion-panel>
              </v-expansion-panels>
            </v-card-text>
          </div>

          <v-divider></v-divider>
          <div v-if="task_rs['local'].length > 0">
            <v-card-title>
              <span class="text-h6">Local Explaination</span>
            </v-card-title>
            <v-card-text>
              <v-expansion-panels variant="popout">
                <v-expansion-panel
                  v-for="sample in task_rs['local']"
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
        </v-container>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
import { TransitionGroup } from "vue";

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

function isJson(str) {
  try {
    JSON.parse(str);
  } catch (e) {
    return false;
  }
  return true;
}
function isValidHttpUrl(string) {
  let url;
  try {
    url = new URL(string);
  } catch (_) {
    return false;
  }
  return url.protocol === "http:" || url.protocol === "https:";
}

export default {
  data: () => ({
    disabled: false,
    typeMap,
    dialog: false,
    tldialog: false,
    trdialog: false,
    sheets: [],
    tasks: [],
    task_rs: {
      global: [],
      local: [],
    },
    valid: true,
    urlRules: [
      (v) => !!v || "URL is required",
      (v) => isValidHttpUrl(v) || "Invalid URL",
    ],
    infoRules: [
      (v) => !!v || "Information is required",
      (v) => isJson(v) || "Should be in JSON format",
    ],
    dbSrviceList: [],
    xaiSrviceList: [],
    modelSrviceList: [],
    evaluationSrviceList: [],
    task_sheet_name: "",
    task_type: "",
    explanation_task_ticket: "",
    model_service_executor_id: "",
    xai_service_executor_id: "",
    db_service_executor_id: "",
    evaluation_service_executor_id: "",
    task_parameters: "{}",
    current_task_sheet_id: "",
    taskListIntv: undefined,
  }),
  methods: {
    timestampFormat(ts) {
      if (ts === "" || ts === undefined) {
        return "";
      }
      return ts;
    },
    getTaskStatus(item) {
      return item.start_time !== undefined && item.task_status === "initialized"
        ? "stopped"
        : item.task_status;
    },
    deleteTaskSheet(item) {
      this.ax.post(
        "http://127.0.0.1:5006/task_publisher/task_sheet",
        {
          act: "delete",
          task_sheet_id: item.task_sheet_id,
        },
        {
          success: (response) => {
            this.fetchTaskSheetList();
          },
          error: () => {},
          final: () => {},
        }
      );
    },
    closeTaskResultDialog() {
      this.trdialog = false;
    },
    showTaskResult(item) {
      this.trdialog = true;
      // console.log(item);
      this.ax.get(
        "http://127.0.0.1:5006/task_publisher/task_result",
        {
          task_ticket: item.task_ticket,
        },
        {
          success: (response) => {
            let localRs = [];
            // console.log(response.data["local"]);
            for (const [key, value] of Object.entries(response.data["local"])) {
              localRs.push({
                sample_name: key,
                explanation_results: value,
              });
            }
            this.task_rs["local"] = localRs;
            let globalRs = [];
            for (const i of response.data["global"]) {
              if (i.file_type === "img") {
                globalRs.push(i);
              }
            }
            this.task_rs["global"] = globalRs;
          },
          error: () => {},
          final: () => {},
        }
      );
    },
    deleteATask(item) {
      this.ax.post(
        "http://127.0.0.1:5006/task_publisher/task",
        {
          act: "delete",
          task_ticket: item.task_ticket,
        },
        {
          success: (response) => {},
          error: () => {},
          final: () => {
            this.fetchTaskList(this.current_task_sheet_id);
          },
        }
      );
    },
    stopATask(item) {
      this.ax.post(
        "http://127.0.0.1:5006/task_publisher/task",
        {
          act: "stop",
          task_ticket: item.task_ticket,
        },
        {
          success: (response) => {},
          error: () => {},
          final: () => {
            this.fetchTaskList(this.current_task_sheet_id);
          },
        }
      );
    },
    runTaskFromTaskSheet() {
      console.log(this.current_task_sheet_id);
      this.ax.post(
        "http://127.0.0.1:5006/task_publisher/task_sheet",
        {
          act: "run",
          task_sheet_id: this.current_task_sheet_id,
        },
        {
          success: (response) => {
            console.log(response.data);
          },
          error: () => {},
          final: () => {
            this.fetchTaskList(this.current_task_sheet_id);
            // this.closeTaskDialog();
          },
        }
      );
    },
    fetchTaskList(task_sheet_id) {
      console.log("fetch task list");
      this.ax.get(
        "http://127.0.0.1:5006/task_publisher/task",
        {
          task_sheet_id,
        },
        {
          success: (response) => {
            let rs = [];
            let hasRunning = false;
            for (let task of response.data) {
              rs.push(task);
              if (task.task_status === "running") {
                hasRunning = true;
              }
            }
            rs.sort((a, b) => {
              return b.request_time - a.request_time;
            });
            this.tasks = rs;
            clearInterval(this.taskListIntv);
            if (hasRunning) {
              this.taskListIntv = setInterval(() => {
                this.fetchTaskList(task_sheet_id);
              }, 10000);
            }
          },
          error: () => {},
          final: () => {},
        }
      );
    },
    showTaskDialog(item) {
      this.current_task_sheet_id = item.task_sheet_id;
      this.tldialog = true;
      this.fetchTaskList(this.current_task_sheet_id);
    },
    closeTaskDialog() {
      this.tldialog = false;
      this.current_task_sheet_id = "";
      this.tasks = [];
      clearInterval(this.taskListIntv);
    },
    async showTaskSheetDetail(item) {
      this.openD();
      this.disabled = true;
      this.task_sheet_name = item.task_sheet_name;
      this.task_type = typeMap[item.task_type];
      this.model_service_executor_id = item.model_service_executor_id;
      this.xai_service_executor_id = item.xai_service_executor_id;
      this.db_service_executor_id = item.db_service_executor_id;
      this.evaluation_service_executor_id = item.evaluation_service_executor_id;
      this.task_parameters = JSON.stringify(item.task_parameters);
    },
    fetchServiceList() {
      this.ax.get(
        "http://127.0.0.1:5006/task_publisher/executor",
        {},
        {
          success: (response) => {
            // console.log(response.data);
            const newDBList = [];
            const newXAIList = [];
            const newModelList = [];
            const newEvaluationList = [];
            for (const item of response.data) {
              if (item.executor_type === "db") {
                newDBList.push(item);
              }
              if (item.executor_type === "xai") {
                newXAIList.push(item);
              }
              if (item.executor_type === "model") {
                newModelList.push(item);
              }
              if (item.executor_type === "evaluation") {
                newEvaluationList.push(item);
              }
            }
            this.dbSrviceList = newDBList;
            this.xaiSrviceList = newXAIList;
            this.modelSrviceList = newModelList;
            this.evaluationSrviceList = newEvaluationList;
          },
          error: () => {},
          final: () => {},
        }
      );
    },
    resetForm() {
      this.task_sheet_name = "";
      this.task_type = "";
      this.model_service_executor_id = "";
      this.xai_service_executor_id = "";
      this.db_service_executor_id = "";
      this.evaluation_service_executor_id = "";
      this.explanation_task_ticket = "";
      this.task_parameters = "{}";
    },
    openD() {
      this.disabled = false;
      this.resetForm();
      this.dialog = true;
      this.fetchServiceList();
    },
    closeD() {
      this.dialog = false;
    },
    async submitAction(e) {
      // this.validate();
      e.preventDefault();
      const { valid } = await this.$refs.form.validate();
      console.log(valid);
      const task_sheet_name = this.task_sheet_name;
      const task_type = typeMap[this.task_type];
      const model_service_executor_id = this.model_service_executor_id;
      const xai_service_executor_id = this.xai_service_executor_id;
      const db_service_executor_id = this.db_service_executor_id;
      const evaluation_service_executor_id =
        this.evaluation_service_executor_id;
      let task_parameters = this.task_parameters;
      // const explanation_task_ticket = this.explanation_task_ticket;
      // if (task_type === "evaluation") {
      //   let param = JSON.parse(task_parameters);
      //   param["explanation_task_ticket"] = explanation_task_ticket;
      //   task_parameters = JSON.stringify(param);
      // }
      // console.log(task_sheet_name);
      // console.log(task_type);
      // console.log(db_service_executor_id);
      // console.log(model_service_executor_id);
      // console.log(xai_service_executor_id);
      // console.log(evaluation_service_executor_id);
      // console.log(task_parameters);
      if (valid) {
        this.ax.post(
          "http://127.0.0.1:5006/task_publisher/task_sheet",
          {
            act: "create",
            task_sheet_name,
            task_type,
            db_service_executor_id,
            model_service_executor_id,
            xai_service_executor_id,
            evaluation_service_executor_id,
            task_parameters,
          },
          {
            success: (response) => {
              console.log(response.data);
            },
            error: () => {},
            final: () => {
              this.fetchTaskSheetList();
              this.closeD();
            },
          }
        );
      }
    },
    fetchTaskSheetList() {
      console.log("fetch task sheet list");
      this.ax.get(
        "http://127.0.0.1:5006/task_publisher/task_sheet",
        {},
        {
          success: (response) => {
            // console.log(response.data);
            const newList = response.data;
            this.sheets = newList;
          },
          error: () => {},
          final: () => {},
        }
      );
    },
  },
  mounted: function () {
    // console.log(123);
    this.fetchTaskSheetList();
  },
  components: { TransitionGroup },
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
