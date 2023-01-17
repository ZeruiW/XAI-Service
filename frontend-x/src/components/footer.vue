<template>
  <v-footer
    id="footer"
    padless
    height="30"
    :class="{
      footer: isAbs,
      'd-flex': true,
      'align-center': true,
      'justify-center': true,
    }"
  >
    <div style="font-size: 15px">
      <strong>2023 - Concordia University - ConcordiaSAC Research Lab</strong>
    </div>
  </v-footer>
</template>

<script>
export default {
  props: ["abs"],
  computed: {
    isAbs: function () {
      return this.$props.abs !== undefined;
    },
  },
};
</script>

<style scoped>
.footer {
  position: absolute;
  bottom: 0;
  right: 0;
  left: 0;
}
</style>
