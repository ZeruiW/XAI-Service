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
        <col span="1" style="width: 40%" />
        <col span="1" style="width: 30%" />
        <col span="1" style="width: 30%" />
      </colgroup>
      <thead>
        <tr>
          <th class="text-left font-weight-bold">Sheet Name</th>
          <th class="text-left font-weight-bold">Task Type</th>
          <th class="text-left font-weight-bold"></th>
        </tr>
      </thead>
      <tbody>
        <tr class="trHover" v-for="item in sheets" :key="item.name">
          <td>{{ item.task_sheet_name }}</td>
          <td>{{ item.task_type }}</td>
          <td style="text-align: right">
            <v-btn
              color="primary"
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
    <v-dialog
      id="task-sheet-create-dialog"
      contained
      v-model="dialog"
      max-width="600px"
    >
      <v-form
        id="task-sheet-create-form"
        ref="form"
        v-model="valid"
        lazy-validation
        @submit="submitAction"
        :disabled="disabled"
      >
        <v-card>
          <v-card-title>
            <span v-if="!disabled" class="text-h5">New Task Sheet</span>
            <span v-if="disabled" class="text-h5">Task Sheet Detail</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-text-field
                  label="Task Sheet Name*"
                  name="task_sheet_name"
                  v-model="task_sheet_name"
                  :rules="[(v) => !!v || 'Name is required']"
                  required
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
                ></v-select>
              </v-row>
              <v-row>
                <v-textarea
                  name="task_parameters"
                  v-model="task_parameters"
                  label="Task Parameters"
                  :rules="infoRules"
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
        </v-card>
      </v-form>
    </v-dialog>
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
            <v-text-field
              ref="new_task_name"
              variant="underlined"
              label="New Task Name"
              class="mr-3"
              v-model="new_task_name"
              :rules="[(v) => !!v || 'This field is required']"
              style="width: 300px"
            ></v-text-field>

            <v-btn
              size="small"
              variant="outlined"
              color="green-darken-1"
              form="task-sheet-create-form"
              @click="runTaskFromTaskSheet"
            >
              Run a New Task
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
              <col span="1" style="width: 50%" />
              <col span="1" style="width: 15%" />
              <col span="1" style="width: 15%" />
              <col span="1" style="width: 10%" />
            </colgroup>
            <thead>
              <tr>
                <th class="text-left font-weight-bold">Task Name</th>
                <th class="text-left font-weight-bold">Task Ticket</th>
                <th class="text-left font-weight-bold">Start Time</th>
                <th class="text-left font-weight-bold">End Time</th>
                <th class="text-left font-weight-bold">Status</th>
                <th class="text-left font-weight-bold"></th>
              </tr>
            </thead>
            <tbody>
              <tr class="trHover" v-for="item in tasks" :key="item.task_ticket">
                <td>{{ item.task_name }}</td>
                <td>{{ item.task_ticket }}</td>
                <td>{{ item.task_status.formated_start_time }}</td>
                <td>{{ item.task_status.formated_end_time }}</td>
                <td>{{ item.task_status.task_status }}</td>
                <td style="text-align: right">
                  <v-btn
                    v-if="item.task_status.task_status === 'finished'"
                    style="margin-left: 0.5em"
                    color="blue"
                    size="x-small"
                    prepend-icon="mdi-clipboard-minus-outline"
                    @click="showTaskResult(item)"
                    >Result</v-btn
                  >
                  <v-btn
                    v-if="item.task_status.task_status === 'running'"
                    style="margin-left: 0.5em"
                    color="error"
                    size="x-small"
                    prepend-icon="mdi-close"
                    @click="stopATask(item)"
                    >Stop</v-btn
                  >
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-card-text>
      </v-card>
    </v-dialog>

    <v-dialog
      id="task-result-dialog"
      style="height: 100%"
      contained
      v-model="trdialog"
    >
      <v-card style="height: 100000px">
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
                <th class="text-left font-weight-bold">File Name</th>
                <th class="text-left font-weight-bold">Content</th>
              </tr>
            </thead>
            <tbody>
              <tr
                class="trHover"
                v-for="item in task_rs['global']"
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
                <th class="text-left font-weight-bold">File Name</th>
                <th class="text-left font-weight-bold">Content</th>
              </tr>
            </thead>
            <tbody>
              <tr
                class="trHover"
                v-for="item in task_rs['local']"
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
    model_service_executor_id: "",
    xai_service_executor_id: "",
    db_service_executor_id: "",
    evaluation_service_executor_id: "",
    task_parameters: "{}",
    current_task_sheet_id: "",
    new_task_name: "",
    taskListIntv: undefined,
  }),
  methods: {
    deleteTaskSheet(item) {
      this.ax.post(
        "http://127.0.0.1:5006/task_publisher/task_sheet",
        {
          act: "del",
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
            for (const i of response.data["local"]) {
              if (i.file_type === "img") {
                localRs.push(i);
              }
            }
            localRs.sort();
            this.task_rs["local"] = localRs;

            let globalRs = [];
            for (const i of response.data["global"]) {
              if (i.file_type === "img") {
                globalRs.push(i);
              }
            }
            globalRs.sort();
            this.task_rs["global"] = globalRs;
          },
          error: () => {},
          final: () => {},
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
      this.$refs.new_task_name.validate().then((v) => {
        if (v[0] === undefined) {
          // valid
          this.ax.post(
            "http://127.0.0.1:5006/task_publisher/task_sheet",
            {
              act: "run",
              task_sheet_id: this.current_task_sheet_id,
              task_name: this.new_task_name,
            },
            {
              success: (response) => {
                console.log(response.data);
              },
              error: () => {},
              final: () => {
                this.fetchTaskList(this.current_task_sheet_id);
                // this.closeTaskDialog();
                this.new_task_name = "";
              },
            }
          );
        }
      });
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
            for (let key of Object.keys(response.data)) {
              rs.push(response.data[key]);
              if (response.data[key].task_status.task_status === "running") {
                hasRunning = true;
              }
            }
            rs.sort((a, b) => {
              return b.task_status.start_time - a.task_status.start_time;
            });
            this.tasks = rs;
            clearInterval(this.taskListIntv);
            if (hasRunning) {
              this.taskListIntv = setInterval(() => {
                this.fetchTaskList(task_sheet_id);
              }, 1000);
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
      const task_sheet_name = this.task_sheet_name;
      const task_type = typeMap[this.task_type];
      const model_service_executor_id = this.model_service_executor_id;
      const xai_service_executor_id = this.xai_service_executor_id;
      const db_service_executor_id = this.db_service_executor_id;
      const evaluation_service_executor_id =
        this.evaluation_service_executor_id;
      const task_parameters = this.task_parameters;

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
};
</script>

<style></style>
