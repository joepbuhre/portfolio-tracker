<template>
    <div class="flex fixed inset-0 justify-center items-center bg-black bg-opacity-20 backdrop-blur-sm" v-if="showLogin" @click.self="showLogin = false">
        <div class="bg-white shadow-lg w-[500px] h-[300px] rounded-md flex justify-center items-center px-10">
            <div class="w-full">
                <label for="accountid">Put in your unique accountnumber</label>
                <div class="flex w-full">
                    <input 
                        :type="showAccountId ? 'text' : 'password'"
                        name="accountid" 
                        id="accountid"
                        autocomplete="username"
                        v-model="accountNumber" 
                        placeholder="test" 
                        class="w-full border border-solid border-gray-200 rounded-sm px-2 py-1 rounded-tr-none border-r-0" 
                        />
                    <button @click="toggleShowAccountId" class="border-gray-200 border border-solid px-3">
                        <EyeOffIcon v-if="showAccountId" />
                        <Eye v-else />
                    </button>
                </div>

                <button class="mt-2 bg-blue-600 text-white px-2 py-1 rounded-sm" @click="login">Submit</button>
                <button class="mt-2 bg-blue-600 text-white px-2 py-1 rounded-sm ml-2" @click="createAccount">Create Account</button>

            </div>
        </div>
    </div>
    <div class="flex">
        <div class="w-1/5">
            <input type="file" v-on:change="handleFile">
            <div class="flex gap-5 mt-3 mb-10">
                <button class="bg-slate-200 rounded-md border border-solid border-slate-600 px-4 py-1" @click="populateTables">submit</button>
                <button class="bg-slate-200 rounded-md border border-solid border-slate-600 px-4 py-1" @click="fetchStocks">Fetch Stocks</button>
            </div>
            <button @click="showAccountValues = !showAccountValues" class="flex gap-2">
                <EyeOffIcon v-if="showAccountValues" />
                <Eye v-else />
                <p>
                    <span v-if="showAccountValues">Hide</span><span v-else>Show</span><span>&nbsp;Account values</span>
                </p>
            </button>
            <div v-for="groupby in groupbys">
                <input type="checkbox" v-model="selectGroupbys" :value="groupby" :id="groupby">
                <label class="capitalize pl-2" :for="groupby">{{ groupby }}</label>
            </div>
        </div>
        <div class="w-full grid grid-cols-1 gap-3">
            <div v-for="dfType in resp" class="py-2">
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

<style>
.hideAccountValues th:nth-of-type(2), 
.hideAccountValues th:nth-of-type(3), 
.hideAccountValues td:nth-of-type(2), 
.hideAccountValues td:nth-of-type(3) {
    display: none;
}
</style>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api } from "../utils/api";
import { AxiosResponse } from "axios";
import { Eye, EyeOffIcon } from 'lucide-vue-next'


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
    description: string;
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

const fetchStocks = () => {
    resp.value = [];
    
    [...selectGroupbys.value, 'description'].forEach((el) => {
        console.log(el)
        api.get(`/stocks/${el}`,{headers: {'x-userid': accountNumber.value}} ).then((res: AxiosResponse) => {
            resp.value.push({
                name: el,
                data: res.data,
            });
        });
    });

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

// Handle account here
const accountNumber = ref<string | null>(null);
const showLogin = ref<boolean>(true);
const showAccountId = ref<boolean>(false)
const showAccountValues = ref<boolean>(true)


const toggleShowAccountId = () => showAccountId.value = !showAccountId.value

const createAccount = () => {
    api.post('/create-account').then(res => {
        const data: {uuid: string} = res.data
        accountNumber.value = data.uuid
    })
}

const login = () => {
    api.post('/login',{}, {
        headers: {
            'x-userid': accountNumber.value
        }
    }).then(res => {
        const data: {success: boolean} = res.data
        showLogin.value = false
    }).catch(err => {
        // TODO Error
    })
}

</script>
