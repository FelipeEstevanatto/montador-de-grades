<script setup>
import { ref, watch, computed, onMounted, toRaw } from "vue";
import axios from "axios";
import deburr from "lodash/deburr";
import TextInput from "./TextInput.vue";
import CustomButton from "./CustomButton.vue";

const props = defineProps({
  selectedList: {
    type: Array,
    required: true,
  },
  horario: {
    type: String,
    required: false,
  },
  dia: {
    type: String,
    required: false,
  },
  show_not_avaliable: {
    type: Boolean,
    required: false,
  },
});
const emit = defineEmits(["updateValue"]);

const itensFiltered = ref([]);
const allUnfilteredDisciplines = ref([]);
const search = ref("");
const isListEmpty = ref(false);

const COLOR_BLUE = "#385F73";
const COLOR_RED = "#FF0000";
const base_address = "https://www.unifesp.br/campus/sjc/images/sjc/Secretaria_de_Gradua%C3%A7%C3%A3o/UCs_Vigentes/";

onMounted(async () => {
  await fetchDisciplinas();
  await updateData();
});

watch(
  [props.selectedList, search],
  async () => {
    await updateData();
    filterSearch();
  },
  { deep: true }
);

watch(
  () => props.show_not_avaliable,
  (newVal, oldVal) => {
    //console.log('show_not_avaliable changed from', oldVal, 'to', newVal);
    // You can add your logic here
    updateData();
  }
)

// Function that fetches the disciplines from the server
async function fetchDisciplinas() {
  try {
    const { data } = await axios.get("/src/data/disciplinas.json");

    allUnfilteredDisciplines.value = data.map((item) => ({
      ...item,
      COLOR: COLOR_RED,
    }));
  } catch (error) {
    console.log(error);
  }
}

// Function that updates the data based on the selected disciplines
async function updateData() {
  //const selectedList = toRaw(props.selectedList);
  const ids = selectedIdsList.value;
  itensFiltered.value = allUnfilteredDisciplines.value.filter(filterSubject);

  if (props.show_not_avaliable) {
    isListEmpty.value = itensFiltered.value.length === 0;
    return;
  }

  // Remove the already selected disciplines from the list
  itensFiltered.value = itensFiltered.value.filter((item) => {
    // Check if the item ID is included in the ids array or if there's a discipline with the same name
    return !ids.includes(item.ID) && !ids.some((id) => {
      const selectedDiscipline = allUnfilteredDisciplines.value.find(
        (discipline) => discipline.ID === id
      );
      return selectedDiscipline.NOME === item.NOME;
    });
  });

  // Remove disciplines in the same time slot as the selected ones
  const selectedDisciplines = allUnfilteredDisciplines.value.filter((item) =>
    ids.includes(item.ID)
  );
  const selectedTimes = selectedDisciplines.flatMap((item) =>
    item.HORARIO.map((horario, index) => `${item.DIA[index]}-${horario}`)
  );
  itensFiltered.value = itensFiltered.value.filter((item) => {
    const times = item.HORARIO.map((horario, index) => `${item.DIA[index]}-${horario}`);
    return !times.some((time) => selectedTimes.includes(time));
  });


  isListEmpty.value = itensFiltered.value.length === 0;
}

// Filter the items based on the search input
function filterSearch() {
  if (search === "") {
    return;
  }

  const query = search.value.toLowerCase();
  const regex = /[\u0300-\u036f]/g;
  const normalizedQuery = query.normalize("NFD").replace(regex, "");
  itensFiltered.value = itensFiltered.value.filter((item) => {
    const normalizedItemName = item.NOME.normalize("NFD").replace(regex, "");
    return deburr(normalizedItemName).toLowerCase().includes(deburr(normalizedQuery));
  });
  isListEmpty.value = itensFiltered.value.length === 0;
}

// Function that opens the pdf file of the discipline
function description(obj) {
  // retira todos os textos entre parênteses ou colchetes e substitui os espaços por underline
  const name = obj.NOME.replace(/\s*\([^)]*\)/g, "").replace(/ /g, "_");

  window.open(base_address + name[0] + "/" + name + ".pdf", "_blank");
}

// Function that filters the disciplines for that specific day and time
function filterSubject(item) {
  if (props.horario === null && props.dia === null) {
    return true;
  }

  const hasTime = props.horario ? item.HORARIO.includes(props.horario) : true;
  const hasDay = props.dia ? item.DIA.includes(props.dia) : true;

  return hasTime && hasDay;
}

function emitValue(item) {
  emit("updateValue", item);
  updateData()
}

// Format time to be displayed
function format_time(item) {
  return item.DIA.map((dia, index) => `${dia} - ${item.HORARIO[index]}`).join("\r\n");
}

const selectedIdsList = computed(() =>
  props.selectedList.map((item) => item.ID)
);
</script>

<template>
  <div class="normal-case px-4 pb-4 flex-auto text-xs font-normal tracking-wide">
    <TextInput
      density="compact"
      placeholder="Pesquise a disciplina desejada..."
      append-inner-icon="mdi-checkbox-marked-circle"
      @search="search = $event"
    ></TextInput>
  </div>
  <div class="overflow-auto max-h-[300px]">
    <div v-if="isListEmpty" class="w-full flex align-center justify-center">
      <h3 class="block text-xl font-bold">Nenhuma disciplina disponível</h3>
    </div>
    <div v-else v-for="item in itensFiltered" :key="item.ID">
      <div  class="grow basis-0 w-full p-3 flex-0100 max-w-full">
        <div class="bg-cardbackground rounded text-white shadow-md">
          <div
            class="v-card-title block flex-none font-medium min-w-0 overflow-hidden text-ellipsis normal-case whitespace-nowrap break-normal h6"
          >
            {{ item.NOME }}
          </div>
          <div
            class="normal-case flex-auto text-xs font-normal tracking-wide px-4 pb-4 pt-0"
          >
            <span
              class="text-white font-mono whitespace-pre-wrap text-base lista-horario"
              >{{ format_time(item) }}</span
            ><br />
            <span>Professores/Turma: {{ item.PROFESSORES }} - {{ item.TURMA }}</span>
          </div>

          <div  class="px-2 py-2 tracking-widerx flex *:rounded *:border-1 *:border-white">
            <CustomButton
              class="px-2 h-9 mr-2 border-solid uppercase font-medium"
              @click="emitValue(item)"
            >
              Adicionar
            </CustomButton>
            <CustomButton
              class="px-2 h-9 uppercase"
              @click="description(item)"
            >
              Descrição
            </CustomButton>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.v-card-title {
  font-size: 1.25rem;
  -webkit-hyphens: auto;
  hyphens: auto;
  letter-spacing: 0.0125em;
  padding: 0.5rem 1rem;
  word-wrap: break-word;
}
</style>