<template>
  <v-card
    class="mx-auto"
    style="height: 100%; height: 100%; display: flex; flex-direction: column"
    :elevation="3"
  >
    <template v-slot:title>
      <div class="clearfix">
        <div style="width: 50%; float: left; padding: 0.1em">
          Provenance Graph
        </div>
      </div>
    </template>
    <v-divider></v-divider>
    <v-card-text>
      <div id="graphbox"></div>
      <div id="controls">
        <v-btn id="zinbtn" size="small" class="ml-2" variant="outlined">
          <v-icon icon="mdi-magnify-plus-outline"></v-icon
        ></v-btn>
        <v-btn id="zoutbtn" size="small" class="ml-2" variant="outlined">
          <v-icon icon="mdi-magnify-minus-outline"></v-icon
        ></v-btn>
        <v-btn id="rsbtn" size="small" class="ml-2" variant="outlined">
          <v-icon icon="mdi-autorenew"></v-icon
        ></v-btn>
      </div>
    </v-card-text>

    <Transition name="fade" mode="out-in">
      <v-card
        theme="dark"
        id="nodeDetails"
        v-if="viewNodeDetails"
        class="mx-auto"
        width="600"
        height="500"
        prepend-icon="mdi-home"
        :style="{
          top: nodeDetailY + 'px',
          left: nodeDetailX + 'px',
        }"
        @mouseenter="nodeDetailsActivated = true"
        @mouseleave="
          (e) => {
            nodeDetailsActivated = false;
          }
        "
      >
        <template v-slot:title>
          <v-btn size="small" style="float: left">
            {{ currentNode.attributes.node_type }} |
            {{ currentNode.key }}</v-btn
          >
          <Transition name="fade" mode="out-in">
            <v-btn
              v-if="nodeDetailsActivated"
              size="small"
              color="error"
              varient="outline"
              style="float: right"
              @click="hideNodeDetails(true)"
            >
              <v-icon icon="mdi-close"></v-icon
            ></v-btn>
          </Transition>
        </template>

        <v-card-text style="overflow-y: auto">
          <v-table density="compact">
            <thead>
              <tr>
                <th class="text-left">Key</th>
                <th class="text-left">Value</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="attrKey in Object.keys(currentNode.attributes.info)"
                :key="attrKey"
              >
                <td>{{ attrKey }}</td>
                <td>{{ currentNode.attributes.info[attrKey] }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-card-text>
      </v-card>
    </Transition>
  </v-card>
</template>

<script>
import Graph from "graphology";
import Sigma from "sigma";
import { circular, random, circlepack } from "graphology-layout";
import ForceSupervisor from "graphology-layout-force/worker";
import forceLayout from "graphology-layout-force";
import forceAtlas2 from "graphology-layout-forceatlas2";
import FA2Layout from "graphology-layout-forceatlas2/worker";
import noverlap from "graphology-layout-noverlap";
import NoverlapLayout from "graphology-layout-noverlap/worker";

export default {
  data: () => ({
    viewNodeDetails: false,
    nodeDetailsActivated: false,
    nodeActivated: false,
    nodeDetailX: 0,
    nodeDetailY: 0,
    showNodeDetailsTimeOut: undefined,
    hideNodeDetailsTimeOut: undefined,
    renderer: undefined,
    layout: undefined,
    provenance: {},
    graph: undefined,
    currentNode: undefined,
  }),
  methods: {
    showNodeDetails(node_key) {
      this.graph.forEachNode((node, attributes) => {
        if (node === node_key) {
          this.currentNode = {
            key: node,
            attributes,
          };
        }
      });
      this.viewNodeDetails = true;
      clearTimeout(this.showNodeDetailsTimeOut);
      clearTimeout(this.hideNodeDetailsTimeOut);
      this.showNodeDetailsTimeOut = setTimeout(() => {
        if (!this.nodeDetailsActivated) {
          this.hideNodeDetails();
        }
      }, 1500);
    },
    hideNodeDetails(im = false) {
      clearTimeout(this.showNodeDetailsTimeOut);
      clearTimeout(this.hideNodeDetailsTimeOut);
      if (im) {
        this.viewNodeDetails = false;
        this.nodeDetailsActivated = false;
      } else {
        this.hideNodeDetailsTimeOut = setTimeout(() => {
          if (!this.nodeDetailsActivated && !this.nodeActivated) {
            this.viewNodeDetails = false;
            this.nodeDetailsActivated = false;
          }
        }, 500);
      }
    },
    getProvenance(cb) {
      console.log("fetch provenance");
      this.ax.get(
        "http://127.0.0.1:5006/task_publisher/provenance",
        {},
        {
          success: (response) => {
            this.provenance = response.data;
            if (cb !== undefined) {
              cb();
            }
          },
          error: () => {},
          final: () => {
            console.log(JSON.parse(JSON.stringify(this.provenance)));
          },
        }
      );
    },
    renderCamara() {
      const camera = this.renderer.getCamera();

      // Bind zoom manipulation buttons
      document.getElementById("zinbtn").addEventListener("click", () => {
        camera.animatedZoom({ duration: 300 });
      });
      document.getElementById("zoutbtn").addEventListener("click", () => {
        camera.animatedUnzoom({ duration: 300 });
      });
      document.getElementById("rsbtn").addEventListener("click", () => {
        camera.animatedReset({ duration: 300 });
      });
    },
    renderNodeEvents() {
      const nodeEvents = [
        "enterNode",
        "leaveNode",
        "downNode",
        "clickNode",
        "rightClickNode",
        "doubleClickNode",
        "wheelNode",
      ];

      const thiz = this;

      nodeEvents.forEach((eventType) => {
        thiz.renderer.on(eventType, (e) => {
          // console.log(e);
          // console.log(eventType, e.node);

          if (eventType === "enterNode") {
            // var d = thiz.renderer.getNodeDisplayData(e.node);
            var posX = e.event.original.clientX;
            var posY = e.event.original.clientY;

            var mainPanelEl = document.getElementsByClassName("mainPanel")[0];
            var mainPanelLeft = mainPanelEl.getBoundingClientRect().left;

            var mainPanelTop = mainPanelEl.getBoundingClientRect().top;

            var mainPanelTopPadding = Number(
              getComputedStyle(mainPanelEl).paddingTop.replace("px", "")
            );
            var mainPanelLetfPadding = Number(
              getComputedStyle(mainPanelEl).paddingLeft.replace("px", "")
            );

            thiz.nodeDetailX = posX - mainPanelLeft - mainPanelLetfPadding;
            thiz.nodeDetailY = posY - mainPanelTop - mainPanelTopPadding;
            thiz.nodeActivated = true;
            thiz.showNodeDetails(e.node);
          }
          if (eventType === "leaveNode") {
            thiz.nodeActivated = false;
            thiz.hideNodeDetails();
          }
        });
      });
    },
    renderEdgeEvents() {
      const thiz = this;

      this.renderer.on("enterEdge", ({ edge }) => {
        thiz.hoveredEdge = edge;
        thiz.renderer.refresh();
      });
      this.renderer.on("leaveEdge", ({ edge }) => {
        thiz.hoveredEdge = null;
        thiz.renderer.refresh();
      });
    },
    createNodesAndEdges() {
      // Create a sample graph
      const graph = new Graph();

      const executors = this.provenance.executors;

      for (const executor of executors) {
        delete executor._id;
        graph.addNode(`${executor.executor_id}`, {
          color: "blue",
          size: 15,
          label: executor.executor_endpoint_url,
          info: executor,
          node_type: "executor",
        });
      }

      const taskSheets = this.provenance.task_sheets;

      for (const tasksheet of taskSheets) {
        delete tasksheet._id;
        graph.addNode(`${tasksheet.task_sheet_id}`, {
          color: "grey",
          size: 10,
          label: `Task Sheet: ${tasksheet.task_sheet_name}`,
          info: tasksheet,
          node_type: "tasksheet",
        });

        if (tasksheet.model_service_executor_id !== "") {
          graph.addEdge(
            tasksheet.task_sheet_id,
            tasksheet.model_service_executor_id,
            { type: "arrow", label: "usesModelExecutor", size: 5 }
          );
        }
        if (tasksheet.db_service_executor_id !== "") {
          graph.addEdge(
            tasksheet.task_sheet_id,
            tasksheet.db_service_executor_id,
            { type: "arrow", label: "usesDBExecutor", size: 5 }
          );
        }
        if (tasksheet.xai_service_executor_id !== "") {
          graph.addEdge(
            tasksheet.task_sheet_id,
            tasksheet.xai_service_executor_id,
            { type: "arrow", label: "usesXAIExecutor", size: 5 }
          );
        }
        if (tasksheet.evaluation_service_executor_id !== "") {
          graph.addEdge(
            tasksheet.task_sheet_id,
            tasksheet.evaluation_service_executor_id,
            { type: "arrow", label: "usesEvaluationExecutor", size: 5 }
          );
        }
      }

      const tasks = this.provenance.tasks;

      for (const task of tasks) {
        delete task._id;

        graph.addNode(`${task.task_ticket}`, {
          color: "green",
          size: 10,
          label: `Task: ${task.task_name}`,
          info: task,
          node_type: "task",
        });

        graph.addEdge(task.task_sheet_id, task.task_ticket, {
          type: "arrow",
          label: "hasTask",
          size: 5,
        });
      }

      const pipelines = this.provenance.pipelines;

      for (const pipeline of pipelines) {
        delete pipeline._id;

        graph.addNode(`${pipeline.pipeline_id}`, {
          color: "red",
          size: 20,
          label: `Pipeline: ${pipeline.pipeline_name}`,
          info: pipeline,
          node_type: "pipeline",
        });

        graph.addEdge(pipeline.pipeline_id, pipeline.xai_task_sheet_id, {
          type: "arrow",
          label: "hasXAITaskSheet",
          size: 5,
        });

        graph.addEdge(pipeline.pipeline_id, pipeline.evaluation_task_sheet_id, {
          type: "arrow",
          label: "hasEvaluationTaskSheet",
          size: 5,
        });
      }

      const pipeline_runs = this.provenance.pipeline_runs;

      for (const pipeline_run of pipeline_runs) {
        delete pipeline_run._id;

        graph.addNode(`${pipeline_run.pipeline_run_ticket}`, {
          color: "purple",
          size: 20,
          label: `Pipeline Run: ${pipeline_run.pipeline_run_ticket}`,
          info: pipeline_run,
          node_type: "pipeline_run",
        });

        graph.addEdge(
          pipeline_run.pipeline_run_ticket,
          pipeline_run.xai_task_sheet_id,
          {
            type: "arrow",
            label: "runFromXAITaskSheet",
            size: 5,
          }
        );

        graph.addEdge(
          pipeline_run.pipeline_run_ticket,
          pipeline_run.xai_task_ticket,
          {
            type: "arrow",
            label: "hasXAIResult",
            size: 5,
          }
        );

        graph.addEdge(
          pipeline_run.pipeline_run_ticket,
          pipeline_run.evaluation_task_sheet_id,
          {
            type: "arrow",
            label: "runFromEvaluationTaskSheet",
            size: 5,
          }
        );

        graph.addEdge(
          pipeline_run.pipeline_run_ticket,
          pipeline_run.evaluation_task_ticket,
          {
            type: "arrow",
            label: "hasEvalResult",
            size: 5,
          }
        );

        graph.addEdge(
          pipeline_run.pipeline_id,
          pipeline_run.pipeline_run_ticket,
          {
            type: "arrow",
            label: "hasRun",
            size: 5,
          }
        );
      }

      this.graph = graph;
      return graph;
    },
    renderGraph() {
      const box = document.getElementById("graphbox");

      const graph = this.createNodesAndEdges();

      // random.assign(graph);
      circlepack.assign(graph);
      // circular.assign(graph);

      forceAtlas2.assign(graph, { iterations: 1 });

      const layout = new FA2Layout(graph, {
        settings: { gravity: 0 },
      });

      layout.start();
      this.layout = layout;

      // Create the sigma
      const thiz = this;
      this.renderer = new Sigma(graph, box, {
        renderEdgeLabels: true,
        enableEdgeHoverEvents: "debounce",
        edgeReducer(edge, data) {
          const res = { ...data };
          if (edge === thiz.hoveredEdge) {
            res.color = "#cc1100";
            res.size = 10;
          }
          return res;
        },
      });

      this.renderCamara();
      this.renderNodeEvents();
      this.renderEdgeEvents();
    },
  },
  mounted: function () {
    this.getProvenance(() => {
      try {
        this.renderGraph();
      } catch (error) {
        console.error(error);
      }
    });
  },
  unmounted: function () {
    console.log("unmount prov");
    try {
      this.layout.stop();
      this.layout.kill();
      this.renderer.clear();
      // prevent Too many active WebGL contexts. Oldest context will be lost.
      this.renderer.kill();
    } catch (error) {
      console.error(error);
    }
  },
};
</script>

<style>
.fade-enter-active {
  transition: all 0.2s;
}
.fade-leave-active {
  transition: all 0.2s ease-out;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
#graphbox {
  height: 100%;
  width: 100%;
}
#nodeDetails {
  transition: top 0.8s, left 0.8s, opacity 0.2s;
  /* display: block; */
  list-style: none;
  margin: 0;
  padding: 0;
  position: absolute;
  width: 250px;
  z-index: 999999;
  height: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}
#controls {
  position: absolute;
  right: 1em;
  top: 76px;
}
</style>
