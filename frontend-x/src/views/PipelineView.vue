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
              @click="showPipelineDetail(item)"
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
    pipeline_name: "",
    current_pipeline: "",
    xaiTaskSheetList: [],
    evalTaskSheetList: [],
    current_xai_task_sheet_id: "",
    current_evaluation_task_sheet_id: "",
    current_xai_task_name: "",
    current_evaluation_task_name: "",
  }),
  mounted: function () {
    this.fetchPipeline();
  },
  methods: {
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
                      console.log(123);
                      console.log(this.current_pipeline.pipeline_id);
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
                      console.log(123);
                      console.log(this.current_pipeline.pipeline_id);
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
    showPipelineDetail(item) {
      this.openPDD();
      this.current_pipeline = item;
    },
    openPDD() {
      this.fetchTaskSheetList();
      this.pddialog = true;
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
          final: () => {},
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
