<template>
    <!-- <TheTimeLine>
        
    </TheTimeLine>     -->
    <IuTable
        :rows="data"
        :headers="headers"
        :axios-key="'test1'"
        :axios-instance="test"
    >
        <Column
            v-for="(display, key) of headers"
            :display-name="display.name"
            :column-name="display.name"
            sorting-enabled
        />
    </IuTable>
    <IuTable
        :rows="data2"
        :headers="headers2"
        :axios-key="'test2'"
        :axios-instance="api"
    >
        <Column
            v-for="(display, key) of headers2"
            :display-name="display.name"
            :column-name="display.name"
            sorting-enabled
        />
    </IuTable>
</template>

<script setup lang="ts">
import { Column, IuTable } from "@IuComponentLib/TheTable";
import { Header, HeaderValues } from "@IuComponentLib/TheTable/types";
import TheTimeLine from "@components/TheTimeLine.vue";
import { api } from "@src/utils/api";
import { Axios } from "axios";
import { computed, onMounted, ref } from "vue";

// https://jsonplaceholder.typicode.com/posts

const data = ref<any>([]);

const headers = computed((): Header => {
    return data.value.length > 0
        ? Object.fromEntries(
              Object.keys(data.value[0]).map((el) => {
                  return [
                      el,
                      {
                          name: el,
                      },
                  ];
              }),
          )
        : {};
});
const data2 = ref<any>([]);

const headers2 = computed((): Header => {
    return data2.value.length > 0
        ? Object.fromEntries(
              Object.keys(data2.value[0]).map((el) => {
                  return [
                      el,
                      {
                          name: el,
                      },
                  ];
              }),
          )
        : {};
});

type TestType = ReturnType<typeof api.get>;
const test = ref<TestType | undefined>(undefined);
onMounted(() => {
    test.value = api
        .get("https://jsonplaceholder.typicode.com/posts")
        .then((res) => {
            data.value = res.data;
        })
        .catch((err) => {});

    api.get("https://jsonplaceholder.typicode.com/todfsfaddos")
        .then((res) => {
            data2.value = res.data;
        })
        .catch((err) => {});
});
</script>
