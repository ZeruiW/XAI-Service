<template>
  <v-card class="mx-auto" style="height: 100%" :elevation="3">
    <template v-slot:title>
      <div class="clearfix">
        <div style="width: 50%; float: left; padding: 0.1em">
          Registered Services
        </div>
        <div
          style="width: 50%; float: right; text-align: right; padding: 0.1em"
        >
          <v-btn size="small" color="success" @click="openD"> Register </v-btn>
        </div>
      </div>
    </template>

    <v-divider></v-divider>
    <!-- <v-card-text> This is content </v-card-text> -->
    <v-table>
      <thead>
        <tr>
          <th class="text-left font-weight-bold">Url</th>
          <th class="text-left font-weight-bold">Service Type</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in services" :key="item.name">
          <td>{{ item.url }}</td>
          <td>{{ item.type }}</td>
        </tr>
      </tbody>
    </v-table>
    <v-dialog contained v-model="dialog" max-width="600px" persistent>
      <v-form
        id="service-reg-form"
        ref="form"
        v-model="valid"
        lazy-validation
        @submit="submitAction"
      >
        <v-card>
          <v-card-title>
            <span class="text-h5">New Service</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-text-field
                  label="Service Endpoint URL*"
                  name="url"
                  :rules="urlRules"
                  required
                ></v-text-field>
              </v-row>
              <v-row>
                <v-select
                  label="Service Type*"
                  :items="['Database', 'AI Model', 'XAI', 'Evaluation']"
                  :rules="[(v) => !!v || 'Service type is required']"
                  name="type"
                  required
                ></v-select>
              </v-row>
              <v-row>
                <v-textarea
                  name="info"
                  label="Service Info"
                  :rules="infoRules"
                  model-value='{"exp_name": "name"}'
                ></v-textarea>
              </v-row>
            </v-container>
            <small>*indicates required field</small>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="red-darken-1" @click="closeD"> Close </v-btn>
            <v-btn type="submit" color="green-darken-1" form="service-reg-form">
              Submit
            </v-btn>
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
    typeMap,
    dialog: false,
    services: [],
    valid: true,
    urlRules: [
      (v) => !!v || "URL is required",
      (v) => isValidHttpUrl(v) || "Invalid URL",
    ],
    infoRules: [
      (v) => !!v || "Information is required",
      (v) => isJson(v) || "Should be in JSON format",
    ],
  }),
  methods: {
    openD() {
      this.dialog = true;
    },
    closeD() {
      this.dialog = false;
    },
    async submitAction(e) {
      // this.validate();
      e.preventDefault();
      const { valid } = await this.$refs.form.validate();
      const url = e.target.elements.url.value;
      const type = e.target.elements.type.value;
      const info = e.target.elements.info.value;

      if (valid) {
        // console.log(url);
        // console.log(type);
        // console.log(info);
        this.ax.post(
          "http://127.0.0.1:5006/task_publisher/executor",
          {
            act: "reg",
            executor_endpoint_url: url,
            executor_info: info,
            executor_type: type,
          },
          {
            success: (response) => {
              console.log(response.data);
            },
            error: () => {},
            final: () => {
              this.fetchExecutorList();
              this.closeD();
            },
          }
        );
      }
    },
    async validate() {},
    fetchExecutorList() {
      console.log("fetch service list");
      this.ax.get(
        "http://127.0.0.1:5006/task_publisher/executor",
        {},
        {
          success: (response) => {
            // console.log(response.data);
            const newList = [];
            for (const item of response.data) {
              newList.push({
                url: item.executor_endpoint_url,
                type: this.typeMap[item.executor_type],
              });
            }

            this.services = newList;
          },
          error: () => {},
          final: () => {},
        }
      );
    },
  },
  mounted: function () {
    // console.log(123);
    this.fetchExecutorList();
  },
};
</script>

<style></style>
