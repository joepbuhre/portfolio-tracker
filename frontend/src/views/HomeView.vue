<template>
    <button class="fixed top-2 right-2 flex gap-2" @click="logout">
        <LogOut />
        Logout
    </button>
    <TheLoginModel v-if="showLogin" @success="loginSuccess" class="z-50" />
    <div class="flex">
        <div class="w-1/5">
            <h2 class="text-blue-700 font-bold text-lg flex gap-3">Welcome 
                <span>
                    <Loader2 v-if="main.isLoading" class="animate-spin" />
                    <LineChart v-else />
                </span>
            </h2>
            <input type="file" v-on:change="handleFile">
            <div class="flex gap-5 mt-3 mb-10">
                <button class="bg-blue-700 hover:bg-opacity-80 duration-200 text-white rounded-md border border-solid border-slate-600 px-2 py-1" @click="fetchStocks">Fetch Stocks</button>
                <button class="bg-blue-700 hover:bg-opacity-80 duration-200 text-white rounded-md border border-solid border-slate-600 px-2 py-1" @click="fetchHistory">Fetch History</button>
            </div>
            <button @click="showAccountValues = !showAccountValues" class="flex gap-2">
                <EyeOffIcon v-if="showAccountValues" />
                <Eye v-else />
                <p>
                    <span v-if="showAccountValues">Hide</span><span v-else>Show</span><span>&nbsp;Account values</span>
                </p>
            </button>
            <div v-for="groupby in groupbys">
                <input type="checkbox" v-model="selectGroupbys" :value="groupby.value" :id="groupby.value">
                <label class="capitalize pl-2" :for="groupby.value">{{ groupby.name }}</label>
            </div>
        </div>
        <div class="w-full grid grid-cols-1 gap-3">
            <div class="h-96 rounded-md" :class="{'animate-pulse bg-slate-300 ': Object.keys(history).length === 0}" >
                <GraphLine :history="history" v-if="Object.keys(history).length > 0" />
            </div>
            <div v-for="dfType in respSorted" class="py-2">
                <h4 class="capitalize font-bold">Groupby: {{ dfType.name }}</h4>
                <table class="text-left shadow-lg border border-solid border-blue-200 rounded-md border-spacing-0 border-separate" :class="{hideAccountValues: !showAccountValues}">
                    <thead>
                        <tr class="border-b-slate-800 border-b">
                            <th v-for="col in Object.keys(dfType.data[0])" class="px-10 capitalize" >
                                {{ col }}
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="row in dfType.data" class="hover:bg-slate-200" @mouseover="highLightSeries(row?.ticker?.replace('.', 'x'))" @mouseleave="unHighLightSeries(row?.ticker?.replace('.', 'x'))">
                            <td v-for="(col, colname) in row" class="px-10" >
                                <span v-if="colname === 'percentage'">{{ formatPercentage(<number>col) }}</span>
                                <span v-else-if="colname === 'totalValue'">{{ formatCurrency(<number>col) }}</span>
                                <span v-else>{{ col }}</span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
</div>
</template>

<style>
.hideAccountValues th:nth-of-type(2), 
.hideAccountValues th:nth-of-type(3), 
.hideAccountValues td:nth-of-type(2), 
.hideAccountValues td:nth-of-type(3) {
    display: none;
}
</style>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { api } from "../utils/api";
import { AxiosResponse } from "axios";
import {LogOut, X } from 'lucide-vue-next'
import { useMain } from "../store/main";
import { LineChart } from "lucide-vue-next";
import { Loader2 } from "lucide-vue-next";
import TheLoginModel from "../components/TheLoginModel.vue";
import GraphLine from "../components/GraphLine.vue";
import type {TickerHistory} from '../components/GraphLine.vue'
import { Eye, EyeOffIcon } from "lucide-vue-next";

// Get all group by options
type groupbyOptions = 'ticker-description' | 'description' | 'country' | 'industry' | 'sector' | 'currency' | 'quoteType'

const groupbys = ref<{name: string, value: groupbyOptions}[]>([
     {'name': 'Product', value: 'ticker-description'}
    ,{'name': 'Industry', value: 'industry'}
    ,{'name': 'Sector', value: 'sector'}
    ,{'name': 'Product Type', value: 'quoteType'}
    ,{'name': 'Country', value: 'country'}
    ,{'name': 'Currency', value: 'currency'}
])
const selectGroupbys = ref<groupbyOptions[]>([
     'ticker-description'
    ,'industry'
    ,'sector'
    ,'quoteType'
    ,'country'
    ,'currency'
])

// Store setup
const main = useMain()

interface GroupDf {
    ticker?: string,
    description: string;
    totalValue: number;
    count: number;
    percentage: number;
}

type respType = { name: string; data: GroupDf[] }

const resp = ref<respType[]>([]);

const respSorted = computed((): respType[] => {
    return groupbys.value
        .filter(el => selectGroupbys.value.includes(el.value))
        .filter(el => resp.value.map(el2 => el2.name).includes(el.value))
        .map(el => ({
            name: el.name,
            data: resp.value.filter(el2 => el2.name === el.value)[0].data
        }))
})

const handleFile = (e: Event) => {
    const target = e.target as HTMLInputElement
    if (target?.files?.length && target?.files?.length > 0) {
        file.value = target.files[0]
        populateTables()
    }
}
const file = ref<File | null>(null)
const fileValue = ref<string>('')

const showAccountValues = ref<boolean>(true)

const populateTables = () => {
    resp.value = [];
    
    if(file.value !== null) {      
        const formdata = new FormData()
        formdata.append('file', <File>file.value)
        if(main.getUserId !== null) {
            api.post(`/add-shares`, formdata).then((res: AxiosResponse) => {
                fetchStocks()
            });
        } else {
            [...selectGroupbys.value, 'description'].forEach((el) => {
                api.post(`/stocks/anonymous/${el}`, formdata).then((res: AxiosResponse) => {
                    resp.value.push({
                        name: el,
                        data: res.data,
                    });
                });
            })
        }
    }
}

const fetchStocks = () => {
    resp.value = [];
    
    main.setLoading(true, 'fetchStocks')
    Promise.allSettled(
        [...selectGroupbys.value].map((el) => {
            return new Promise((resolve, reject) => {
                api.get(`/stocks/${el}`,{headers: {'x-userid': main.getUserId}} ).then((res: AxiosResponse) => {
                    resp.value.push({
                        name: el,
                        data: res.data,
                    });
                    resolve(true)
                }).catch(reject)
            })
        })
    ).finally(() => main.setLoading(false, 'fetchStocks'))

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

const showLogin = ref<boolean>(true);

const loginSuccess = () => {
    showLogin.value = false 
    fetchStocks()
    fetchHistory()
}

const logout = () => {
    showLogin.value = true
    resp.value = []
    main.setUserId(null)
}

// Setup history graph here
const tickers = computed(() => null)
const history = ref<{[key: string]: TickerHistory[]}>({})
const fetchHistory = () => {
    api.get('/history').then(res => {
        const data = res.data
        history.value = <{[key: string]: TickerHistory[]}>data
    })
}

// Hightlight functions
const highLightSeries = (seriesName: string | undefined) => {   
    if(seriesName !== undefined) {
        const nonTargets = document.querySelectorAll(`.apexcharts-area-series.apexcharts-plot-series .apexcharts-series:not([seriesName=${seriesName}])`)
        Array.from(nonTargets).forEach(node => node.classList.add('legend-mouseover-inactive'))
    } 
}

const unHighLightSeries = (seriesName: string | undefined) => {
    if(seriesName !== undefined) {
        const nonTargets = document.querySelectorAll(`.apexcharts-area-series.apexcharts-plot-series .apexcharts-series.legend-mouseover-inactive`)
        Array.from(nonTargets).forEach(node => node.classList.remove('legend-mouseover-inactive'))
    } 
}

</script>
