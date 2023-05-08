<template>
    <div class="flex">
        <div class="w-1/5">
            <input type="file" v-on:change="handleFile">
            <div class="flex gap-5 mt-3 mb-10">
                <button class="bg-slate-200 rounded-md border border-solid border-slate-600 px-4 py-1" @click="populateTables">submit</button>
                <button class="bg-slate-200 rounded-md border border-solid border-slate-600 px-4 py-1" @click="purge">Purge</button>
            </div>
            <div v-for="groupby in groupbys">
                <input type="checkbox" v-model="selectGroupbys" :value="groupby" :id="groupby">
                <label class="capitalize pl-2" :for="groupby">{{ groupby }}</label>
            </div>
        </div>
        <div class="w-full grid grid-cols-1 gap-3">
            <div v-for="dfType in resp" class="py-2">
                <h4 class="capitalize font-bold">Groupby: {{ dfType.name }}</h4>
                <table class="text-left shadow-lg border border-solid border-blue-200 rounded-md border-spacing-0 border-separate">
                    <thead>
                        <tr class="border-b-slate-800 border-b">
                            <th v-for="col in Object.keys(dfType.data[0])" class="px-10" >
                                {{ col }}
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="row in dfType.data" class="hover:bg-slate-200">
                            <td v-for="(col, colname) in row" class="px-10" >
                                <span v-if="colname === 'percentage'">{{ formatPercentage(<number>col) }}</span>
                                <span v-else-if="colname === 'currentValue'">{{ formatCurrency(<number>col) }}</span>
                                <span v-else>{{ col }}</span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
</div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api } from "../utils/api";
import { AxiosResponse } from "axios";

// Get all group by options
type groupbyOptions =  'country' | 'industry' | 'sector' | 'currency' | 'quoteType'

const groupbys = ref<groupbyOptions[]>([
    'country'
    ,'industry'
    ,'sector'
    ,'currency'
    ,'quoteType'
])
const selectGroupbys = ref<groupbyOptions[]>([
    'country'
    ,'industry'
    ,'sector'
    ,'currency'
    ,'quoteType'
])

interface GroupDf {
    Product: string;
    currentValue: number;
    Aantal: number;
    percentage: number;
}

const resp = ref<{ name: string; data: GroupDf[] }[]>([]);

const handleFile = (e: Event) => {
    const target = e.target as HTMLInputElement
    target?.files?.[0]?.text().then((res: any) => {
        fileValue.value = res
    })
    if (target?.files?.length && target?.files?.length > 0) {
        file.value = target.files[0]
        populateTables()
    }
}
const file = ref<File | null>(null)
const fileValue = ref<string>('')

const purge = () => {
    api.post('/purge').then(res => alert(res.data))
}

const populateTables = () => {
    resp.value = [];
    
    if(file.value !== null) {      
        [...selectGroupbys.value, 'Product'].forEach((el) => {
            const formdata = new FormData()
            formdata.append('file', <File>file.value)
            api.post(`/dataframe/${el}`, formdata).then((res: AxiosResponse) => {
                resp.value.push({
                    name: el,
                    data: res.data,
                });
            });
        });
    }
}

const formatPercentage = (num: number) => {
    const formatter = new Intl.NumberFormat('nl-NL', {
        style: 'percent',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })

    return formatter.format(num)
}

const formatCurrency = (num: number) => {
    const formatter = new Intl.NumberFormat('nl-NL', {
        style: 'currency',
        currency: 'EUR',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })

    return formatter.format(num)
}

</script>
