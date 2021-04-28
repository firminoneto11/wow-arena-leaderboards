
function get_json() {
    const url = "https://us.api.blizzard.com/data/wow/pvp-season/30/pvp-leaderboard/3v3?namespace=dynamic-us&locale=en_US&access_token=USrrs2dmyy4hwhcOIVCJ7JpNBoA3eCCOYv"
    const br_realms = ['azralon', 'nemesis', 'goldrinn', 'gallywix', 'tol-barad']

    let request = new XMLHttpRequest()
    request.open("GET", url)
    request.send()
    request.onload = () => {
        if (request.status === 200) {
            let json_object = JSON.parse(request.response)
            for (let attribute in json_object) {
                if (attribute === 'entries') {
                    json_object = json_object['entries']
                    break
                }
            }
            let counter = 1

            for (let index in json_object) {
                let char = json_object[index].character
                let rating = json_object[index].rating
                let player_name = char.name

                let faction = json_object[index].faction
                faction = faction.type

                let realm = char.realm
                realm = realm.slug

                for (let r in br_realms) {
                    if (realm === br_realms[r]) {
                        let row = document.createElement('tr')
                        let row_id = `c${counter}`
                        row.id = row_id
                        let showed1 = document.createElement('td')
                        let showed2 = document.createElement('td')
                        let showed3 = document.createElement('td')
                        let showed4 = document.createElement('td')
                        let showed5 = document.createElement('td')
                        showed1.innerHTML = counter
                        showed2.innerHTML = rating
                        showed3.innerHTML = player_name
                        showed4.innerHTML = realm
                        showed5.innerHTML = faction
                        counter = counter + 1
                        document.getElementById('tbody').appendChild(row)
                        document.getElementById(row_id).appendChild(showed1)
                        document.getElementById(row_id).appendChild(showed2)
                        document.getElementById(row_id).appendChild(showed3)
                        document.getElementById(row_id).appendChild(showed4)
                        document.getElementById(row_id).appendChild(showed5)
                    } else {
                        continue
                    }
                }
            }
        } else {
            let error_msg = document.createElement("h2")
            error_msg.innerHTML = "The API isn't working at the moment. Try again later."
            document.body.appendChild(error_msg)
        }
    }

    let main_table = document.getElementById('main_table')
    let button = document.getElementById('button')
    main_table.style.display = 'table'
    button.style.display = 'none'
}
