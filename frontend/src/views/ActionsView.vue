<template>
    <div class="p-8">
        <div class="flex justify-between mb-4">
            <h1 class="font-bold text-xl">Vind hier al je acties</h1>
            <div>
                <button @click="showFileUpload = true" class="bg-blue-700 text-white px-2 py-1 rounded-md">Importeer acties</button>
            </div>
            <TheModal title="Upload file" :show="showFileUpload" @hide="showFileUpload = false">
                <div class="w-full text-center" v-if="uploading">
                    <h3>Uploading file...</h3>
                    <Loader2Icon class="m-auto animate-spin" />
                </div>
                <TheIuUploader v-else @upload="uploadFile" />
            </TheModal>
        </div>
        <div>
            <input type="text" placeholder="search here" v-model="searchVal">
        </div>
        <IuTable :rows="stockActionsComputed">
            <Column
                column-name="purchase_date"
                display-name="Purchase Date"
            />
            <Column column-name="description_share" display-name="Share" :filter-values="stockActionsComputed.map(el => el.description_share)" />
            <Column column-name="description" display-name="action" :filter-values="stockActionsComputed.map(el => el.description)" />
            <Column column-name="home_mutation" display-name="Home Mutation" :formatter="EuroFormatter" />
        </IuTable>
    </div>
</template>
<script setup lang="ts">
import { Column, IuTable } from "@IuComponentLib/TheTable";
import { TheModal } from "@IuComponentLib/TheModal";
import { api } from "@src/utils/api";
import { computed, onMounted, ref } from "vue";
import { DateFormatter, EuroFormatter } from "@src/utils/formatters";
import { TheIuUploader } from "@IuComponentLib/TheUploader";
import { Loader2Icon } from "lucide-vue-next";

const stockActions = ref<StockActions[]>([]);

const stockActionsComputed = computed(() => {
    return stockActions.value.filter(el => {
        return el.description_share.toUpperCase().includes(searchVal.value.toUpperCase())
    })
})

const showFileUpload = ref<boolean>(false)

const uploading = ref<boolean>(false)

const searchVal = ref<string>('')

const fetchActions = () => {
    api.get("/stocks/actions").then((res: any) => {
        const data: StockActions[] = res.data;
        stockActions.value = data;
    });
}

onMounted(() => {
    fetchActions()
});

const uploadFile = (file: File) => {
    uploading.value = true
    const formdata = new FormData()
    formdata.append('file', file)
    api.post('/importer/degiro', formdata)
        .then(res => {
            fetchActions();
            showFileUpload.value = false
        })
        .catch(err => {
            // TODO
        })
        .finally(() => {
            uploading.value = false
        })
}

</script>
