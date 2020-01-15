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
</style>

<template>
    <el-dialog :title="dialog.username" :visible.sync="visible">
        <el-row v-for="message in dialog.messages" :key="message.id">
            <el-col span="16" :offset="message.sender_name==dialog.username? 0:8">
                <div :class="message.sender_name==dialog.username ? 'message-come' : 'message-go'" >
                    <div class="message-content">
                        {{message.content}}
                    </div>
                    <div class="message-info">
                        {{message.sender_name}} | {{message.send_time}}
                    </div>
                </div>
            </el-col>
        </el-row>
        <hr>
        <el-input type="textarea" placeholder="请输入内容" v-model="text"></el-input>
        <el-button type="primary" @click="sendMessage">发送</el-button>
    </el-dialog>
</template>

<script>
export default {
    props: {
        dialog: Object,
        visible: false
    },
    watch: {
        visible() {
            this.$emit('update:visible', this.visible)
        }
    },
    data() {
        return {
            text: ''
        }
    },
    methods: {
        sendMessage() {
            var data = {
                user_id: this.dialog.user_id,
                content: this.text
            }
            var obj = this;
            this.$axios.post('/api/usercenter/messages', data).then(function(res) {
                obj.$message.success('发送成功');
                obj.text = '';
                obj.$emit('send-message');
                obj.visible = false;
            }).catch(function(err) {
                obj.$message.error('发送失败');
            })
        }
    }
}
</script>
