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
      <strong>FALL2021 - Concordia University - COEN6311 Group Super</strong>
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
/* .footer {
  position: absolute;
  bottom: 0;
  right: 0;
  left: 0;
} */
</style>
