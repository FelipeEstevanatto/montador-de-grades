<template>
  <!-- Div mãe -->
  <div class="font-sans p-4 w-full lg:max-w-[90%] mx-auto">
    <!-- Container pra tabela e lateral -->
    <div class="-m-3 flex flex-auto flex-wrap">
      <div class="lg:flex-0666 lg:max-w-[66%] w-full p-3 flex-0100 max-w-full">
        <div class="v-card shadow-md overflow-x-auto grid grid-rows-1 gap-2.5 w-auto">
          <!-- Tabela -->
          <table id="canvas" class="w-full border-collapse">
            <thead class="bg-[#ddd]">
              <tr>
                <th class="border-solid border-1 border-black">Horário</th>
                <th
                  class="border-solid border-1 border-black"
                  v-for="value in daysOfWeek"
                >
                  {{ value }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, rowIndex) in table" class="even:bg-gray-100">
                <td class="whitespace-nowrap border-solid border-1 border-black">
                  {{ hours[rowIndex] }}
                </td>
                <td
                  v-for="(value, colIndex) in row"
                  @click="showAlert(rowIndex, colIndex)"
                  class="whitespace-nowrap border-1 border-solid border-[#302727] hover:cursor-pointer hover:bg-teal-100"
                >
                  <div
                    class="text-[100%] flex flex-col gap-y-1 w-full whitespace-pre-wrap border-collapse"
                  >
                    <div class="">
                      {{ value.NAME }}
                    </div>
                    <div>{{ value.CLASS_INFO }} - {{ value.PROFESSORS }}</div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          <!-- Botões interação -->
          <div
            class="flex flex-row w-full align-content-space-around justify-center whitespace-nowrap"
          >
            <CustomButton
              class="border-red-700 px-4 mr-1 text-red-700"
              @click="cleanAll()"
            >
              Limpar grade<font-awesome-icon
                class="pl-1 text-base text-red-darken-2"
                icon="fa-solid fa-xmark"
              />
            </CustomButton>
            <CustomButton
              class="border-green-600 px-4 mr-1 text-green-600"
              @click="screenShot()"
            >
              Salvar como png
            </CustomButton>

            <CustomButton class="border-black px-4 mr-1" @click="save">
              Exportar
            </CustomButton>

            <CustomButton class="border-black px-4 mr-1" @click="load">
              Importar
            </CustomButton>
          </div>
          <span></span>
        </div>
      </div>
      <!-- Disciplinas escolhidas e disponíveis -->
      <div class="lg:flex-0333 lg:max-w-[33%] p-3 flex-0100 w-full p-3 flex-0100">
        <div class="v-card p-2 shadow-lg">
          <div
            class="p-4 w-full mx-auto lg:max-w-4xl xl:max-w-7xl mx-auto flex sm:block flex-col"
          >
            <!-- Disciplinas Escolhidas: -->
            <div class="-m-3 flex flex-auto flex-wrap bg-white mb-10 sm:-m-3 order-2">
              <div class="grow basis-0 w-full p-3">
                <h3 class="font-bold block text-xl m-0">Disciplinas Escolhidas:</h3>
                Total de Créditos: {{ credits * 2 }}
                <div
                  class="v-card shadow-lg p-2 bg-white overflow-y-scroll h-[300px] rounded"
                >
                  <div class="v-card mx-auto mb-2" v-for="value in SelectedIdsList">
                    <div class="border-1 border-black rounded">
                      <div class="px-4 py-3">
                        <div
                          class="text-xs text-overline mb-1 tracking-widest2x uppercase"
                        >
                          Turma - {{ value.CLASS_INFO }}
                        </div>
                        <div
                          class="normal-case font-sans text-xl font-medium leading-8 mb-1"
                        >
                          {{ value.NAME }}
                        </div>
                        <div
                          class="text-2xs font-normal leading-5 tracking-wide font-sans normal-case"
                        >
                          Professor(a): {{ value.PROFESSORS }}
                        </div>
                      </div>
                      <div class="min-h-[52px] flex flex-none items-center p-2">
                        <CustomButton class="border-black p-2" @click="removeUC(value)">
                          Excluir
                        </CustomButton>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <!-- Disciplinas Disponíveis: -->
            <div class="-mx-3 -mb-3 mt-3 flex flex-auto flex-wrap bg-white mb-10">
              <div class="grow basis-0 w-full p-3 flex flex-col justify-center gap-y-1.5">
                <h3 class="block text-xl font-bold">Disciplinas Disponíveis:</h3>
                <div class="">
                  <ListaUC
                    :show_not_avaliable="btn_state"
                    :horario="null"
                    :dia="null"
                    :selectedList="SelectedIdsList"
                    @updateValue="updateValue"
                  ></ListaUC>
                </div>
                <Switch
                  v-model="btn_state"
                  text="Mostrar Disciplinas Indisponíveis"
                  id="btn_state"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div
      class="mt-3 -m-3 flex flex-auto flex-wrap flex-column align-center justify-center"
    >
      <Alert
        v-model="alert"
        title="Problemas?"
        close-label="Close Alert"
        color="deep-purple-accent-4"
      >
        Faça um pull request em<a href="https://github.com/vpedrota/montador-de-grades"
          ><font-awesome-icon
            class="mx-1 align-middle text-3xl text-grey-darken-4"
            icon="fa-brands fa-github" /></a
        >ou mande uma mensagem para <strong>montadordegrades@gmail.com</strong>.
      </Alert>
    </div>
  </div>

  <Modal v-if="showModal" @close="showModal = false" :title="modalTitle">
    <ListaUC
      :horario="hours[this.row]"
      :dia="daysOfWeek[this.col]"
      :selectedList="SelectedIdsList"
      @updateValue="updateValue"
    ></ListaUC>
  </Modal>
</template>

<script>
var FileData;
var ListId;
var thisObjAlias;

import ModalButton from "./components/ModalButton.vue";
import Modal from "@/components/Modal.vue";
import ListaUC from "./components/Lista.vue";
import html2canvas from "html2canvas";
import Alert from "./components/Alert.vue";
import CustomButton from "./components/CustomButton.vue";
import Switch from "./components/Switch.vue";

export default {
  components: {
    ModalButton,
    Modal,
    ListaUC,
    Alert,
    CustomButton,
    Switch,
  },
  name: "App",
  data() {
    return {
      alert: true,
      showModal: false,
      table: Array.from({ length: 6 }, () => Array(6).fill("")),
      col: 0,
      row: 0,
      credits: 0,
      btn_state: false,
      // O controle das disciplinas será através dos ids das disciplinas
      SelectedIdsList: JSON.parse(localStorage.SelectedIdsList || "[]"),
    };
  },
  computed: {
    daysOfWeek() {
      return ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"];
    },
    hours() {
      return [
        "08h00-10h00",
        "10h00-12h00",
        "13h30-15h30",
        "15h30-17h30",
        "19h00-21h00",
        "21h00-23h00",
      ];
    },
  },
  mounted() {
    this.credits = 0;
    this.SelectedIdsList.forEach((value) => {
      this.updateTable(value, value);
      this.credits += value.HOUR.length;
    });
  },
  methods: {
    showAlert(rowIndex, colIndex) {
      const cellValue = this.table[rowIndex][colIndex];

      if (cellValue === "") {
        this.row = rowIndex;
        this.col = colIndex;
        this.modalTitle = `Disciplinas diponíveis para ${this.daysOfWeek[colIndex]} ${this.hours[rowIndex]}`;
        this.showModal = true;
        return;
      }

      // Removendo matéria
      const selectedSubject = this.SelectedIdsList.find(
        (item) => item.ID === cellValue.ID
      );
      const selectedSubjectIndex = this.SelectedIdsList.indexOf(selectedSubject);
      const selectedSubjectHours = selectedSubject.HOUR.length;

      this.credits -= selectedSubjectHours;
      this.SelectedIdsList.splice(selectedSubjectIndex, 1);
      localStorage.SelectedIdsList = JSON.stringify(this.SelectedIdsList);

      for (let i = 0; i < cellValue.DAY.length; i++) {
        const dayIndex = this.daysOfWeek.indexOf(cellValue.DAY[i]);
        const hourIndex = this.hours.indexOf(cellValue.HOUR[i]);
        this.table[hourIndex][dayIndex] = "";
      }

      this.table[rowIndex][colIndex] = "";

      return;
    },
    // Updates the table with the selected subjects
    updateTable(object, value) {
      object.DAY.forEach((dia) => {
        const diaIndex = this.daysOfWeek.indexOf(dia);

        object.HOUR.forEach((horario) => {
          const horarioIndex = this.hours.indexOf(horario);
          this.table[horarioIndex][diaIndex] = value;
        });
      });
    },
    updateValue(value) {
      this.updateTable(value, value);

      if (this.SelectedIdsList.some((item) => item.ID == value.ID)) {
        return;
      }
      this.SelectedIdsList.push(value);
      localStorage.SelectedIdsList = JSON.stringify(this.SelectedIdsList);

      this.showModal = false;
      this.credits += value.HOUR.length;
    },

    cleanAll() {
      this.SelectedIdsList.splice(0, this.SelectedIdsList.length);
      localStorage.SelectedIdsList = JSON.stringify(this.SelectedIdsList);
      for (let i = 0; i < 6; i++) {
        for (let j = 0; j < 6; j++) {
          this.table[i][j] = "";
        }
      }
      this.credits = 0;
    },
    removeUC(obj) {
      this.SelectedIdsList.splice(this.SelectedIdsList.indexOf(obj), 1);
      localStorage.SelectedIdsList = JSON.stringify(this.SelectedIdsList);
      this.updateTable(obj, "");
      this.credits -= obj.HOUR.length;
    },
    save() {
      const UcsSelecionadasToJson = JSON.stringify(this.SelectedIdsList);
      const aux = document.createElement("a");
      const file = new Blob([UcsSelecionadasToJson], { type: "text/json" });
      aux.href = URL.createObjectURL(file);
      const currentDateTime = new Date().toLocaleString().replace(",", "");
      aux.download = `SelectedUCS ${currentDateTime}.json`;
      aux.click();
    },
    load() {
      var inputFileDocument = document.createElement("input");
      inputFileDocument.setAttribute("type", "file");
      inputFileDocument.setAttribute("id", "upload");
      inputFileDocument.addEventListener(
        "change",
        (event) => {
          ListId = this.SelectedIdsList;
          thisObjAlias = this;
          var reader = new FileReader();
          reader.readAsText(inputFileDocument.files[0]);
          reader.onload = () => {
            FileData = reader.result;
            loadtoTableAfterParse();
          };
        },
        false
      );
      inputFileDocument.click();
    },
    screenShot() {
      let div = document.getElementById("canvas");
      // Use the html2canvas to take a screenshot at 2x device pixel ratio
      // and append it to the output div
      window.devicePixelRatio = 2;
      html2canvas(div).then((canvas) => {
        const image = canvas
          .toDataURL("image/png")
          .replace("image/png", "image/octet-stream");
        const aux = document.createElement("a");
        const currentDateTime = new Date().toLocaleString().replace(",", "");
        aux.setAttribute("download", `UCS-ScreenShot ${currentDateTime}.png`);
        aux.setAttribute("href", image);
        aux.click();
        canvas.remove();
      });
    },
  },
};

function loadtoTableAfterParse() {
  ListId = JSON.parse(FileData);
  thisObjAlias.SelectedIdsList = [];
  localStorage.SelectedIdsList = thisObjAlias.SelectedIdsList;
  ListId.forEach((value) => {
    thisObjAlias.updateTable(value, value);
    thisObjAlias.SelectedIdsList.push(value);
    localStorage.SelectedIdsList = thisObjAlias.SelectedIdsList;
    thisObjAlias.credits += value.HOUR.length;
  });

  thisObjAlias = undefined;
  FileData = undefined;
  ListId = undefined;
}
</script>

<style>
@import url("./style.css");
</style>
