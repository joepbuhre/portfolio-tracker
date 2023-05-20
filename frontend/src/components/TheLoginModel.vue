<template>
    <div
        class="flex fixed inset-0 justify-center items-center bg-black bg-opacity-20 backdrop-blur-sm"
    >
        <div
            class="bg-white shadow-lg w-[500px] h-[300px] rounded-md flex justify-center items-center px-10 relative"
        >
            <button class="absolute top-2 right-2" @click="emits('failed', false)">
                <X />
            </button>
            <div class="w-full">
                <form @submit.prevent="login">
                    <label for="accountid"
                        >Put in your unique accountnumber</label
                    >
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
                        <button
                            @click="toggleShowAccountId"
                            class="border-gray-200 border border-solid px-3"
                        >
                            <EyeOffIcon v-if="showAccountId" />
                            <Eye v-else />
                        </button>
                    </div>

                    <button
                        class="mt-2 bg-blue-600 text-white px-2 py-1 rounded-sm"
                        @click="login"
                        type="submit"
                    >
                        Submit
                    </button>
                    <button
                        class="mt-2 bg-blue-600 text-white px-2 py-1 rounded-sm ml-2"
                        @click="createAccount"
                    >
                        Create Account
                    </button>
                </form>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useMain } from '../store/main';
import { api } from '../utils/api';
import { Eye,EyeOffIcon, X } from 'lucide-vue-next';


const main = useMain()

// Emits
const emits = defineEmits<{
    (e: "success", value: boolean): void;
    (e: "failed", value: boolean): void;
}>()

// Handle account here
const accountNumber = ref<string | null>(null);
const showAccountId = ref<boolean>(false)

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
        main.setUserId(<string>accountNumber.value)
        emits('success', true)
    }).catch(err => {
        // TODO Error
    })
}

onMounted(() => {
    const userid = main.getUserId;
    if (userid) {
        accountNumber.value = userid;
        login();
    }
});
</script>
