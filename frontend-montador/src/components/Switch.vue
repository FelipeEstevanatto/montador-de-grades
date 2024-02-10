<script setup>
import { computed } from "vue";

const props = defineProps({
  text: String,
  id: String,
  modelValue: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["update:modelValue"]);

const checked = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
});
</script>

<template>
  <label class=" inline-flex items-center cursor-pointer">
    <div class="relative">
        <input
            type="checkbox"
            class="peer absolute opacity-0 sr-only"
            v-model="checked"
            :id="id"
        />
        <div
            class="bg-primary w-11 h-6 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-500 my-auto"
        ></div>
    </div>
    <span class="ml-3 text-sm uppercase w-full h-auto" v-text="text"></span>
  </label>
</template>
