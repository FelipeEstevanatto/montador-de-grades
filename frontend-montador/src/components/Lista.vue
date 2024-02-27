<script setup>
import { ref, watch, computed, onMounted, toRaw } from "vue";
import jsonDisciplines from "../data/disciplines.json";
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
    updateData();
  }
)

// Function that fetches the disciplines from the server
async function fetchDisciplinas() {
  try {
    allUnfilteredDisciplines.value = jsonDisciplines.map((item) => ({
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
      return selectedDiscipline.NAME === item.NAME;
    });
  });

  // Remove disciplines in the same time slot as the selected ones
  const selectedDisciplines = allUnfilteredDisciplines.value.filter((item) =>
    ids.includes(item.ID)
  );
  const selectedTimes = selectedDisciplines.flatMap((item) =>
    item.HOUR.map((horario, index) => `${item.DAY[index]}-${horario}`)
  );
  itensFiltered.value = itensFiltered.value.filter((item) => {
    const times = item.HOUR.map((horario, index) => `${item.DAY[index]}-${horario}`);
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
    const normalizedItemName = item.NAME.normalize("NFD").replace(regex, "");
    return deburr(normalizedItemName).toLowerCase().includes(deburr(normalizedQuery));
  });
  isListEmpty.value = itensFiltered.value.length === 0;
}

// Function that opens the pdf file of the discipline
function description(obj) {
  // retira todos os textos entre parênteses ou colchetes e substitui os espaços por underline
  const name = obj.NAME.replace(/\s*\([^)]*\)/g, "").replace(/ /g, "_");

  window.open(base_address + name[0] + "/" + name + ".pdf", "_blank");
}

// Function that filters the disciplines for that specific day and time
function filterSubject(item) {
  if (props.horario === null && props.dia === null) {
    return true;
  }

  const hasTime = props.horario ? item.HOUR.includes(props.horario) : true;
  const hasDay = props.dia ? item.DAY.includes(props.dia) : true;

  return hasTime && hasDay;
}

function emitValue(item) {
  emit("updateValue", item);
  updateData()
}

// Format time to be displayed
function format_time(item) {
  return item.DAY.map((dia, index) => `${dia} - ${item.HOUR[index]}`).join("\r\n");
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
            {{ item.NAME }}
          </div>
          <div
            class="normal-case flex-auto text-xs font-normal tracking-wide px-4 pb-4 pt-0"
          >
            <span
              class="text-white font-mono whitespace-pre-wrap text-base"
              >{{ format_time(item) }}</span
            ><br />
            <span>Professores/Turma: {{ item.PROFESSORS }} - {{ item.CLASS_INFO }}</span>
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
<<<<<<< HEAD:src/components/Lista.vue
</style>
=======
</style>

<script>
import axios from 'axios';
import deburr from 'lodash/deburr'
import TextInput from './TextInput.vue';
import CustomButton from './CustomButton.vue';

export default {
  components: {
    TextInput,
    CustomButton,
  },
  props: ['listaSelecionadas', 'horario', 'dia', 'btn_state_change'],
  emits: ["updateValue"],
  data() {
    return {
      picked: '',
      items: [],
      itensFiltered: [],
      allUnfilteredDisciplines: [],
      search: "",
      loading: false,
      vazio: false,
      btn_state:false,
      numeroDeMateriasNaoConflitantes: 0,
      base_address: "https://www.unifesp.br/campus/sjc/images/sjc/Secretaria_de_Gradua%C3%A7%C3%A3o/UCs_Vigentes/"
    };
  },
  mounted() {
    this.fetchDisciplinas();
    this.atualizarDados();
  }, 
  watch:{
    listaSelecionadas: {
      handler: 'atualizarDados',
      deep: true,
    },
    search: {
      handler: 'filtrarItens',
      deep: true,
    },
    btn_state_change: {
      handler: 'filtrarItens',
      deep: true,
    },
  },  
  methods: {
    async fetchDisciplinas() {
      try {
        const { data } = await axios.get('/disciplinas.json', {
          items: []
        });
        this.allUnfilteredDisciplines = data.map(item => ({ ...item, COLOR: '#FF0000' }));
      } catch (error) {
        console.log(error);
      }
    },

    verificaConflitos(disciplinasSelecionadas, todasDisciplinas) {
      return todasDisciplinas.filter((disciplina) => {
        return !disciplinasSelecionadas.some((selecionada) => {
          return selecionada.DIA.some(dia => 
            disciplina.DIA.includes(dia) && selecionada.HORARIO.some(horarioSel => 
              disciplina.HORARIO.includes(horarioSel)
            )
          );
        });
      });
    },
        
    async atualizarDados(){
      const ids = this.listaSelecionadas;
      //alert(ids)
      //alert(JSON.stringify(ids))
     
      try {
        let response = await axios.get('/disciplinas.json');
       
        
        
        let items = this.verificaConflitos(ids, response.data);
        items = items.filter(this.filtraMateria);
        items.forEach(item_2 => item_2.COLOR = '#385F73');
        this.allUnfilteredDisciplines.forEach(item_3 => item_3.COLOR = '#385F73');

        const itensFiltered = items.filter(item_4 => item_4.COLOR !== '#FF0000');
        this.itensFiltered = itensFiltered;
        this.vazio = itensFiltered.length === 0;

        this.allUnfilteredDisciplines.forEach(item_5 => {
          // test if at least one of the items is in the list and the color is not red
          if (!items.some(item_6 => item_6.ID === item_6.ID) && item_5.COLOR !== '#FF0000') {
            item_5.COLOR = '#FF0000';
            this.itensFiltered.push(item_5);
          }
        });
        this.items = items;
        return response;

      } catch (error) {
        console.log(error);
        throw error;
      }
    },
    filtrarItens() {
      if (this.search === '') {
        this.itensFiltered = this.items;
      }

      const query = this.search.toLowerCase();
      const regex = /[\u0300-\u036f]/g;
      const normalizedQuery = query.normalize('NFD').replace(regex, '');

      this.itensFiltered = this.items.filter(item => {
        const normalizedItemName = item.NOME.normalize('NFD').replace(regex, '');
        return deburr(normalizedItemName).toLowerCase().includes(deburr(normalizedQuery));
      });

      this.vazio = this.itensFiltered.length === 0;
    },
    descricao(obj){
      // retira todos os textos entre parênteses ou colchetes e substitui os espaços por underline
      const nome = obj.NOME.replace(/\s*\([^)]*\)/g, '').replace(/ /g, '_');
      window.open(this.base_address + nome[0] + "/" + nome + ".pdf", "_blank");
    },
    filtraMateria(item) {
      if (this.horario === null && this.dia === null) {
        return true;
      }

      const hasHorario = this.horario ? item.HORARIO.includes(this.horario) : true;
      const hasDia = this.dia ? item.DIA.includes(this.dia) : true;

      return hasHorario && hasDia;
    },
    emitValue(item) {
      this.loading = true;
      this.$emit('updateValue', item);
      this.atualizarDados().finally(() => {
        this.loading = false;
      });
    },
    formata_horario(item) {
      return item.DIA.map((dia, index) => `${dia} - ${item.HORARIO[index]}`).join('\r\n');
    }
  },
  computed: {
    listaSelecionadasIds() {
      return this.listaSelecionadas.map(item => item.ID);
    },
  },
};

</script>
>>>>>>> 225096f502480d37c4045beacad6e432ea31121f:frontend-montador/src/components/Lista.vue
