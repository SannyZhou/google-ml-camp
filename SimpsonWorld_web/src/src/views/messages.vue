<style>
    .message-come {
        text-align: left;
    }
    .message-go {
        text-align: right;
    }
    .message-content {
        font-size: 120%;
        white-space: pre-line
    }
    .message-info {
        color: darkgray;
    }
    .message-card {
        margin: 8px;;
    }
</style>

<template>
    <el-main class="content">
        <el-card class="message-card" v-for="(dialog, index) in dialogs" :key="dialog.user_id">
            <div slot="header">
                <span>{{dialog.username}}</span>
                <el-button style="float: right" type="text" @click="viewDialog(index)">查看</el-button>
            </div>
            <el-row v-for="message in dialog.messages" :key="message.id">
                <el-col span="16" :offset="message.sender_name==dialog.username? 0:8">
                <div :class="message.sender_name==dialog.username ? 'message-come' : 'message-go'">
                    <div class="message-content">
                        {{message.content}}
                    </div>
                    <div class="message-info">
                        {{message.sender_name}} | {{message.send_time}}
                    </div>
                </div>
                </el-col>
            </el-row>
        </el-card>
        <Dialog :visible.sync="dialog_show" :dialog="dialog_sel" v-on:send-message="getMessages"></Dialog>
    </el-main>
</template>

<script>
import Dialog from "./dialog.vue";

export default {
    components: {
        Dialog
    },
    data() {
        return {
            dialog_show: false,
            dialog_sel: {},
            dialogs: []
        }
    },
    methods: {
        viewDialog(index) {
            this.dialog_sel = this.dialogs[index];
            this.dialog_show = true;
        },
        getMessages() {
            var obj = this;
            this.$axios.get('/api/usercenter/messages').then(function(res) {
                obj.dialogs = res.data;
            })
        }
    },
    beforeRouteEnter(to, from, next) {
        next(
            obj => {
                obj.getMessages();
            }
        )
    }
}
</script>
