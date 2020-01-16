<template>
    <div class='showmsg' id='showmsg' v-if="msgCount() == 0"></div>
</template>

<script>
export default {
    data(){
        return{

        }
    },
    computed:{
        msgCount(){
            var type = this.$store.state.msgtype;
            var msg = this.$store.state.msgcontent;
            if (msg !== ""){
                var param = {'msgtype': type, 'message': msg}
                console.log('message param:', param)
                this.$message(param);
            }
            return this.$store.state.msgcount;
        }
    }
}
</script>
