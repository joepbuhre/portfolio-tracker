<template>
    <button
        class="bg-blue-700 hover:bg-opacity-80 duration-200 text-white rounded-md border border-solid border-slate-600 px-2 py-1"
        @click="saveTickers"
    >
        Save tickers
    </button>
    <div class="flex md:px-32">
        <table class="min-w-full ">
            <thead class="bg-white border-b">
                <tr>
                    <th
                        scope="col"
                        class="text-sm font-medium text-gray-900 px-6 py-4 text-left"
                    >
                        ID
                    </th>
                    <th
                        scope="col"
                        class="text-sm font-medium text-gray-900 px-6 py-4 text-left"
                    >
                        ISIN
                    </th>
                    <th
                        scope="col"
                        class="text-sm font-medium text-gray-900 px-6 py-4 text-left"
                    >
                        Description
                    </th>
                    <th
                        scope="col"
                        class="text-sm font-medium text-gray-900 px-6 py-4 text-left"
                    >
                        Market
                    </th>
                    <th
                        scope="col"
                        class="text-sm font-medium text-gray-900 px-6 py-4 text-left"
                    >
                        Ticker
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr
                    v-for="row in res"
                    class="odd:bg-gray-100 even:bg-white border-b"
                >
                    <td
                        class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900"
                    >
                        {{ row.id }}
                    </td>
                    <td
                        class="text-sm text-gray-900 font-light px-6 py-4 whitespace-nowrap"
                    >
                        {{ row.isin }}
                    </td>
                    <td
                        class="text-sm text-gray-900 font-light px-6 py-4 whitespace-nowrap"
                    >
                        {{ row.description }}
                    </td>
                    <td
                        class="text-sm text-gray-900 font-light px-6 py-4 whitespace-nowrap"
                    >
                        {{ row.market }}
                    </td>
                    <td
                        class="text-sm text-gray-900 font-light px-6 py-4 whitespace-nowrap"
                    >
                        <input
                            v-model="changedShares[row.id]"
                            :name="row.id"
                            class="bg-transparent placeholder:text-gray-300 outline-none border-b border-b-black"
                            placeholder="put in ticker"
                        />
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api } from "../utils/api";

interface share_info {
    id: string;
    isin: string;
    description: string;
    market: string;
    ticker: string;
}

const res = ref<share_info[]>([]);

const changedShares = ref<{ [key: string]: string }>({});

onMounted(() => {
    api.get("/stocks")
    .then((result) => {
        res.value = result.data;
        changedShares.value = Object.fromEntries(result.data.map((el: share_info) => ([
            el.id,
            el.ticker
        ])))
    });
})

const saveTickers = () => {
    const saveObj = Object.entries(changedShares.value)
        .map(el => ({
            share_id: el[0],
            ticker: el[1]
        }))
        .filter(el => el.ticker !== null && el.ticker !== '')
    
    api.post("/match-ticker", saveObj)
        .then((res) => {
            alert("saved!");
        })
        .catch((err) => {
            alert(err.data);
        });
};
</script>
