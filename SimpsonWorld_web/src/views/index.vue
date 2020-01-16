<template>
	<div class="index">
		<div class="tip">
			<router-link to="/">
	            <img class="logo-img" src='../../static/simpson_head.jpg'>
            </router-link>
        </div>

		<div class="methods">
			<div class="item" @click="uploadpage" ref="uploadp">
				<img class="img" src="../assets/filedir.png"><h2 class="txt">Upload</h2>
			</div>
		</div>
		<div class="panel" v-if="show">
			<el-upload 
				class="upload-avator"
				action="simpson"
				:show-file-list="false"
				:before-upload="beforeUpload"
				:on-change="fileChange"
				:auto-upload="false">
				<img v-if="simpson.imageBase64" :src="simpson.imageBase64" class="avator">
				<i v-else class="el-icon-plus avatar-uploader-icon"></i>
            </el-upload>
			<br>
			<div class="description">
				<h2 class="text">Now I Want To Say:</h2>
				<input id="introtxt" type="textarea" rows=3 v-model="simpson.description" style="font-weight: color: #EEE; text-align:left; font-size: 16px;">
				<br>
				<button :class="{'active': simpson.imageBase64}" id="btnsubmit" @click="submit">To be simpson!</button>
			</div>
			<div class="cancel"><img src='../common/assets/cross_icon.png' class="icon-cross" @click="cancelcamera"></div>

			<div v-if="showresult" class="panel">
				<div class="rolling">
					<div v-for="item in lists" :key="item.id" class="resultpic">
						<img v-bind:src="`data:image/png;base64,${item.cropped_face}`">
						<img v-bind:src="`data:image/png;base64,${item.simpson_look}`">
						<div class="classname">
							<span class="Fixed">You're</span> <span class="SimpsonName"> {{item.simpson_person}}</span>
							<h2> What will you say? </h2>							
						</div>
						<div class="SimpsonWords">
							<div class="simpsonsays">{{item.simpson_talk}}</div>
						</div>
					</div>
				</div>
				<div class="cancel"><img src='../common/assets/cross_icon.png' class="icon-cross" @click="cancelresult"></div>

			</div>
			<!-- <img v-for="item in scope.row.pictures":src="item" width="40" height="40" class="head_pic" /> -->
			<!-- <img :src="`data:image/png;base64,${img.encodedImage}`" /> -->
		</div>
	</div>
</template>



<script>
import showmsg from './showmsg'


export default {
	data () {
		return {
			fileReader: '',
			file: '',
			show: false,
			show2: false,
			showresult: false,
			loginForm:{username: '', password: ''},
			user_id: 0,
			isLogin:false,
			showpngurl:'../common/assets/hide2.png',
			dialogVisible: false,
			simpson: {
                    name: '',
                    description: 'Today is an interesting day',
                    imageBase64: '',
                    imageFileName: '', 
                    others: [],
				},
			lists: [{
					cropped_face: '',
					simpson_look: '',
					simpson_person: '',
					simpson_talk: '',
				}
			]
		}
	},
	components: {
	},
	created: function(){
	},
	methods: {
		close () {
		},
		cancelcamera () {
			this.show = false
		},
		cancelresult () {
			this.showresult = false
		},
		cancelupload (){
			this.show2 = false
		},
		camerapage () {
			this.show = false
			this.show2 = true
		},
		fileChange(file) {
            
            if ( file ) {
            var fileReader = new FileReader ();
            
            fileReader.readAsDataURL(file.raw)
            fileReader.onload = (fileEvent) => {
                var base64str = ''
                var filename = '' 
                base64str = fileEvent.target.result
                filename = file.name
                this.simpson.imageBase64 = base64str
                this.simpson.imageFileName = filename
            //console.log(fileEvent.target.result);//fileEvent.target.result就是base64路径，上传时当字符串传就行了。
            //console.log(base64str)
            //console.log(this.simpson.imageBase64)
            //console.log(this.simpson.imageFileName)
            };
            }
    
        },
		beforeUpload(file) {
            const isJPG = file.type === 'image/jpeg';
            const isGIF = file.type === 'image/gif';
            const isPNG = file.type === 'image/png';
            const isBMP = file.type === 'image/bmp';
            const isLt2M = file.size / 1024 / 1024 < 2;
 
            if (!isJPG && !isGIF && !isPNG && !isBMP) {
                this.$message.error('上传图片必须是JPG/GIF/PNG/BMP 格式!');
            }
            if (!isLt2M) {
                this.$message.error('上传图片大小不能超过 2MB!');
            }
            return (isJPG || isBMP || isGIF || isPNG) && isLt2M;
		},
		submit () {
			var simpson = {
				name: this.simpson.name, 
				description: this.simpson.description,
				imageBase64: this.simpson.imageBase64,
				others: this.simpson.others,
			}
			setTimeout(() => {
				var obj = this
				this.$axios.post('/api/upload', simpson).then(function (response) {
						console.log(response);
						console.log(response.data)
						obj.lists = response.data
						obj.showresult = true

					}).catch(function (error) {
						console.log(simpson)
						console.log(error);
				});
			}, 8000)
			// .then((res) => {
			// 	console.log(res)
			// 	this.$message.success("Upload success")
			// 	this.$message({
            // 		message: "Waitting for output~"
        	// 	});
			// }).catch(function(err){
			// 	this.$message.error("Upload fail");
			// });
		},
		uploadpage () {
			this.show = true
			this.show2=false
			// this.$store.dispatch('login', this.loginForm);
			// setTimeout(() => {
			// 	console.log(this.$store.state.msgtype,  this.$store.state.msgcontent);
			// 	let type = this.$store.state.msgtype;
			// 	let msg = this.$store.state.msgcontent;
			// 	let msgcontenttype = this.$store.state.msgcontenttype;
			// 	if (msg !== "" && msgcontenttype === 'login'){
			// 		var param = {'type': type, 'message': msg};
			// 		console.log('message param:', param);
			// 		this.$notify(param);
			// 	}else{
			// 		this.$message({
			// 			message: '加载失败！',
			// 			type: 'error'
			// 		});
			// 		return;
			// 	}
			// 	if (this.$store.state.isLogin){
			// 		if (this.$route.query.redirect === undefined || this.$route.query.redirect === ''){
			// 			this.$router.replace('/my');
			// 		}else{
			// 			this.$router.replace(this.$route.query.redirect);
			// 		}
			// 	}
			// }, 800)
		},
		description () {
			this.show = true
		},
	},
	activated :function() {
		this.show2 = false
		this.show = false
	},
	computed: {
		data () {
		}
	}
}
</script>

<style lang="stylus" rel="stylesheet/styl" scoped>
.index
	background #FFF
	.tip{
		height: 300px;
		text-align:center;
		line-height: 50px;
		font-size: 30px;
		font-weight: bold;
		background: #0098da;
		vertical-align: middle;
		.logo-img {
        	margin: 1x 1px;
        	vertical-align: middle;
        	width: px;
        	height: 300px;
    	}
	    .logo-text {
	        margin: 2px;
	        color: white;
	        font-size: x-min;
	        vertical-align: middle;
	    }
	}
	.methods{
		margin-top: 40px;
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		.item{
			width: 40%
			margin-top 30px
			display: flex;
			justify-content: center;
			align-items: center;
			padding: 10px 10px;
			height: 50px;
			border: 2px solid #49422e;
			border-radius: 65px;
			margin-bottom: 30px;
			.txt{
				color: #59422e;
				font-size: x-max;
				margin-top: 5%;
				margin-bottom: 5%;
				text-align: center;
			}
			.img{
				margin-right: 5%;
				margin-top: 5%;
				margin-bottom: 5%;
				height: 90%;
			}
		}
	}
	.panel
		position fixed
		top 0%
		width 100%
		height 100%
		background url("../../static/simpson8.jpg") 0px 0px
		background-size 100%
		vertical-align middle
		.upload-avator
			position relative
			top 10%
			margin:0 auto
			border 1px dashed #d9d9d9
			width 178px
			height 178px
			border-radius 6px
			cursor pointer
			overflow hidden
			text-align center
			background url("../../static/simpson7.jpeg")  0px 0px
			background-size 105%
			.avatar-uploader-icon
				position relative
				top 50%
				margin:0 auto
				font-size 28px
				color #8c939d
				width 100%
				height 100%
				line-height 100%
			.avator
				width 178px
				height 178px
				display block
		.content
			display flex
			flex-wrap wrap
			.prof-item
				flex 0 0 20%
				display block
				font-size 14px
				color #000
				padding 6px 0
				.avatar, .name
					display block
					text-align center
		.description
			position relative
			top 5%
			text-align center
			margin:5px auto
			align-items center
			text
				padding 10px 0
				position relative
				h2
					flex 0 0 60px
					display inline-block
					font-size 20px
					line-height 32px
					color #8f8f8f
				input
					width 300px
					height 40px
					border 1px solid #f2f2f2
					padding 5px
					border-radius 10px
					outline none
			button
				margin-top 25px
				outline none
				border none
				color #FFF
				padding 4px
				font-size 20px
				border-radius 10px
				width 25%
				height 40px
				background #59422e
		.panel
			position fixed
			top 0%
			width 1440px
			height 800px
			overflow hidden
			background url("../../static/simpson8.jpg") 0px 0px
			background-size 100%
			.rolling
				position fixed
				top 60px
				width 1440px
				height 600px
				overflow-y scoll
				overflow-x hidden
				background-color:rgba(255,255,255,0.5)
				.resultpic
					position relative
					margin 20px
					text-align center
					.classname
						position relative
						top 10%
						text-align center
						.Fixed
							font-size 26px
							color #303133
						.SimpsonName
							font-size 26px
							color #800000
					.SimpsonWords
						width 40%
						height 150%
						position relative
						margin:0 auto
						border-radius 10px
						top 3%
						text-align center
						background #F0FFFF
						.simpsonsays
							font-size 24px
							color #606266

		.tologin
			margin-top 25px
			outline none
			padding 4px
			font-size 15px
			border-radius 10px
			width 50%
			height 40px
			text-align center
		.cancel
			position absolute
			bottom 60px
			width 100%
			display block
			text-align center
			.icon-cross :before{
		   		margin 2px 2px
		        vertical-align middle
		        width 45px
		        height 45px
		    }
	
</style>
