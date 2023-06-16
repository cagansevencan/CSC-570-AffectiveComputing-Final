const WebSocket = require('ws');
const EventEmitter = require('events').EventEmitter;

class Cortex extends EventEmitter {
    constructor(user, socketUrl) {
        super()

        // create socket
        process.env['NODE_TLS_REJECT_UNAUTHORIZED'] = 0
        this.socket = new WebSocket(socketUrl)

        this.socket.on('message', (msg) => this.onMessage(msg))
        this.subsriptions = {}
        // read user infor
        this.user = user
    }
    onMessage(msg) {
        const msgObj = JSON.parse(msg)
        const id = msgObj.id
        if (id) return this.emit(id, msgObj)

        Cortex.Streams.forEach((s) => {
            if (s in msgObj) this.emit(`${s}-raw`, msgObj)
        })
    }

    sub(streams) {
        if (streams.every(s => s in this.subsriptions)) return

        this.socket.on('open', async () => {
            await this.checkGrantAccessAndQuerySessionInfo()
            const subResponse = await this.subRequest(streams, this.authToken, this.sessionId)

            const subResponseSuccess = subResponse.result.success

            streams.forEach((s, sIndex) => {
                if (s in this.subsriptions) return
                this.subsriptions[s] = true
                //Listen to raw event only once
                this.on(`${s}-raw`, data => {
                    const formattedData = {}
                    subResponseSuccess[sIndex].cols.forEach((colName, colIndex) => {
                        if (Array.isArray(colName)) {
                            colName.forEach((c, cI) => {
                                formattedData[c] = data[s][colIndex][cI]
                            })
                            return
                        }
                        formattedData[colName] = data[s][colIndex]
                    })
                    if (data.time) {
                        formattedData.time = data.time
                    }

                    data.value = formattedData
                    this.emit(s, data)
                    //cb(data.value)
                })
            })
        })
    }

    subRequest(stream, authToken, sessionId) {
        let socket = this.socket
        const SUB_REQUEST_ID = 6
        let subRequest = {
            "jsonrpc": "2.0",
            "method": "subscribe",
            "params": {
                "cortexToken": authToken,
                "session": sessionId,
                "streams": stream
            },
            "id": SUB_REQUEST_ID
        }
        console.log('sub eeg request: ', subRequest)
        socket.send(JSON.stringify(subRequest))
        return new Promise((resolve, reject) => {
            this.once(SUB_REQUEST_ID, resolve)
        })
    }


    async checkGrantAccessAndQuerySessionInfo() {
        let accessGranted = await this.requestAccess();


        // check if user is logged in CortexUI
        if ("error" in accessGranted) {
            console.log('You must login on CortexUI before request for grant access then rerun')
            throw new Error('You must login on CortexUI before request for grant access')
        } else {
            console.log(accessGranted['result']['message'])
            // console.log(accessGranted['result'])
            if (accessGranted['result']['accessGranted']) {
                await this.querySessionInfo()
            }
            else {
                console.log('You must accept access request from this app on CortexUI then rerun')
                throw new Error('You must accept access request from this app on CortexUI')
            }
        }
    }

    requestAccess() {
        let socket = this.socket
        let user = this.user
        return new Promise((resolve, reject) => {
            const REQUEST_ACCESS_ID = 1
            let requestAccessRequest = {
                "jsonrpc": "2.0",
                "method": "requestAccess",
                "params": {
                    "clientId": user.clientId,
                    "clientSecret": user.clientSecret
                },
                "id": REQUEST_ACCESS_ID
            }

            // console.log('start send request: ',requestAccessRequest)
            socket.send(JSON.stringify(requestAccessRequest));

            this.once(REQUEST_ACCESS_ID, resolve)
        })
    }


    async querySessionInfo() {

        this.headsetId = await this.queryHeadsetId()

        this.ctResult = await this.controlDevice(this.headsetId)
        this.authToken = await this.authorize()
        // const result = JSON.parse(ctResult.toString()).result
        // console.log(result)
        this.sessionId = await this.createSession(this.authToken, this.headsetId)



        console.log('HEADSET ID -----------------------------------')
        console.log(this.headsetId)
        console.log('\r\n')
        console.log('CONNECT STATUS -------------------------------')
        console.log(this.ctResult)
        console.log('\r\n')
        console.log('AUTH TOKEN -----------------------------------')
        console.log(this.authToken)
        console.log('\r\n')
        console.log('SESSION ID -----------------------------------')
        console.log(this.sessionId)
        console.log('\r\n')
    }

    queryHeadsetId() {
        const QUERY_HEADSET_ID = 2
        let socket = this.socket
        let queryHeadsetRequest = {
            "jsonrpc": "2.0",
            "id": QUERY_HEADSET_ID,
            "method": "queryHeadsets",
            "params": {}
        }

        return new Promise((resolve, reject) => {
            socket.send(JSON.stringify(queryHeadsetRequest));
            this.once(QUERY_HEADSET_ID, (data) => {
                try {
                    if (data.result.length > 0) {
                        let headsetId = data.result[0].id
                        resolve(headsetId)
                    }
                    else {
                        console.log('No have any headset, please connect headset with your pc.')
                    }

                } catch (error) { reject(error) }
            })
        })
    }

    controlDevice(headsetId) {
        let socket = this.socket
        const CONTROL_DEVICE_ID = 3
        let controlDeviceRequest = {
            "jsonrpc": "2.0",
            "id": CONTROL_DEVICE_ID,
            "method": "controlDevice",
            "params": {
                "command": "connect",
                "headset": headsetId
            }
        }
        return new Promise((resolve, reject) => {
            socket.send(JSON.stringify(controlDeviceRequest));
            this.once(CONTROL_DEVICE_ID, resolve)
        })
    }


    authorize() {
        let socket = this.socket
        let user = this.user
        return new Promise((resolve, reject) => {
            const AUTHORIZE_ID = 4
            let authorizeRequest = {
                "jsonrpc": "2.0", "method": "authorize",
                "params": {
                    "clientId": user.clientId,
                    "clientSecret": user.clientSecret,
                    "license": user.license,
                    "debit": user.debit
                },
                "id": AUTHORIZE_ID
            }
            socket.send(JSON.stringify(authorizeRequest))
            this.once(AUTHORIZE_ID, (data) => {
                try {
                    let cortexToken = data['result']['cortexToken']
                    resolve(cortexToken)
                } catch (error) { reject(error) }
            })
        });
    }

    createSession(authToken, headsetId) {
        let socket = this.socket
        const CREATE_SESSION_ID = 5
        let createSessionRequest = {
            "jsonrpc": "2.0",
            "id": CREATE_SESSION_ID,
            "method": "createSession",
            "params": {
                "cortexToken": authToken,
                "headset": headsetId,
                "status": "active"
            }
        }
        return new Promise((resolve, reject) => {
            socket.send(JSON.stringify(createSessionRequest));
            this.once(CREATE_SESSION_ID, (data) => {
                try {
                    let sessionId = data['result']['id']
                    resolve(sessionId)
                } catch (error) { reject(error) }
            })
        })
    }

}

Cortex.Streams = ['fac', 'pow', 'eeg', 'mot', 'met', 'com']






module.exports = Cortex