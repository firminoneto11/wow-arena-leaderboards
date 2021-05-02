
String.prototype.toProperCase = function () {
    return this.replace(/\w\S*/g, function (txt) { return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase(); });
};

function get_json(api_key) {
    // Removing the search button
    let button = document.getElementById('button')
    button.style.display = 'none'
    // Showing to the user that his request is ongoing
    let loading = document.createElement('p')
    loading.innerHTML = "Loading the Blizzzard's information. This may take a while..."
    loading.style.color = '#eeeeee'
    loading.style.fontFamily = 'Helvetica'
    loading.style.textAlign = 'center'
    loading.style.marginTop = '1%'
    loading.style.marginBottom = '1%'
    loading.style.fontSize = '1.5rem'

    let main_div = document.getElementsByClassName('main_div')
    main_div = main_div[0]
    main_div.appendChild(loading)

    const url = `https://us.api.blizzard.com/data/wow/pvp-season/30/pvp-leaderboard/3v3?namespace=dynamic-us&locale=en_US&access_token=${api_key}`
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
                        showed4.innerHTML = realm.toProperCase()
                        showed5.innerHTML = faction.toProperCase()
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
            // Removing the loading label
            main_div.removeChild(loading)

            // Displaying the table with the returned data
            let main_table = document.getElementById('main_table')
            main_table.style.display = 'table'

        } else {
            // Removing the loading label
            main_div.removeChild(loading)

            let error_msg = document.createElement('p')
            error_msg.innerHTML = "The API isn't working at the moment. Try again later."
            error_msg.style.color = '#eeeeee'
            error_msg.style.textAlign = 'center'
            error_msg.style.fontFamily = 'Helvetica'
            error_msg.style.fontSize = '1.5rem'
            error_msg.style.marginTop = '1%'
            error_msg.style.marginBottom = '1%'
            main_div.appendChild(error_msg)
        }
    }
}
