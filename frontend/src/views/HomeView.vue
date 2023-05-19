<template>
    <button class="fixed top-2 right-2 flex gap-2" @click="logout">
        <LogOut />
        Logout
    </button>
    <div class="flex fixed inset-0 justify-center items-center bg-black bg-opacity-20 backdrop-blur-sm" v-if="showLogin" @click.self="showLogin = false">
        <div class="bg-white shadow-lg w-[500px] h-[300px] rounded-md flex justify-center items-center px-10 relative">
            <button class="absolute top-2 right-2" @click="showLogin = false">
                <X />
            </button>
            <div class="w-full">
                <form @submit.prevent="login">
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

                    <button class="mt-2 bg-blue-600 text-white px-2 py-1 rounded-sm" @click="login" type="submit">Submit</button>
                    <button class="mt-2 bg-blue-600 text-white px-2 py-1 rounded-sm ml-2" @click="createAccount">Create Account</button>

                </form>
            </div>
        </div>
    </div>
    <div class="flex">
        <div class="w-1/5">
            <h3 class="text-sm text-gray-700">User: {{ accountNumber }}</h3>
            <input type="file" v-on:change="handleFile">
            <div class="flex gap-5 mt-3 mb-10">
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
                <input type="checkbox" v-model="selectGroupbys" :value="groupby.value" :id="groupby.value">
                <label class="capitalize pl-2" :for="groupby.value">{{ groupby.name }}</label>
            </div>
        </div>
        <div class="w-full grid grid-cols-1 gap-3">
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
                        <tr v-for="row in dfType.data" class="hover:bg-slate-200">
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
import { Eye, EyeOffIcon, LogOut, X } from 'lucide-vue-next'
import { useMain } from "../store/main";


// Get all group by options
type groupbyOptions = 'description' | 'country' | 'industry' | 'sector' | 'currency' | 'quoteType'

const groupbys = ref<{name: string, value: groupbyOptions}[]>([
     {'name': 'Product', value: 'description'}
    ,{'name': 'Industry', value: 'industry'}
    ,{'name': 'Sector', value: 'sector'}
    ,{'name': 'Product Type', value: 'quoteType'}
    ,{'name': 'Country', value: 'country'}
    ,{'name': 'Currency', value: 'currency'}
])
const selectGroupbys = ref<groupbyOptions[]>([
     'description'
    ,'industry'
    ,'sector'
    ,'quoteType'
    ,'country'
    ,'currency'
])

// Store setup
const main = useMain()

interface GroupDf {
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

const purge = () => {
    api.post('/purge').then(res => alert(res.data))
}

const populateTables = () => {
    resp.value = [];
    
    if(file.value !== null) {      
        const formdata = new FormData()
        formdata.append('file', <File>file.value)
        if(accountNumber.value !== null) {
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
    
    [...selectGroupbys.value].forEach((el) => {
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

onMounted(() => {
    const userid = main.getUserId
    if(userid) {
        accountNumber.value = userid
        login()
    }
})

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
        main.setUserId(<string>accountNumber.value)
        fetchStocks()
    }).catch(err => {
        // TODO Error
    })
}

const logout = () => {
    showLogin.value = true
    accountNumber.value = null
    resp.value = []
    main.setUserId(null)
}

</script>
