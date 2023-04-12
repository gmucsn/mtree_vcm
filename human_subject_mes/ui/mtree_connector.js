
class MTreeUIManager {
    constructor() {
        console.log("Initializing manager");
    
        this.outlet_1 = "none";

        this.prepare_outlet_connectors();

    }


    prepare_outlet_connectors(){
        var keys = Object.keys(this);
        console.log(keys);
        var result = {};
        

        Object.defineProperty(this, 'outlet_1', {get: () => {console.log("alskfja")}});
        Object.defineProperty(this, 'outlet_1', {set: () => {console.log("alskfja")}});


        // for(var i=0;i<keys.length;i++){
        //     var key = keys[i];
        //     result[key+"_internal"] = this[key];
        //     (function(k){
        //         Object.defineProperty(result,k, {
        //         get:function() {
        //             console.log("getting property:",k);
        //             return this[k + "_internal"];
        //         }, 
        //         set: function(x) { 
        //             console.log("setting property:",k);
        //             this[k + "_internal"] = x 
        //         }
        //         });
        //     })(key)
        // }
        // return result;

    }


}


class ItemValue {
    constructor(unit_number, value) {
        this.unit_number = unit_number;
        this.value = value;
        this.cost = null;
        this.earn = null;
    }

    update(cost){
        this.cost = cost;
        this.earn = this.value - this.cost;
    }

    display_row(){
        var new_row = "<tr id='item_value_" + this.unit_number + "'>"
        new_row += "<td id='item_value_" + this.unit_number + "_unit'>" + this.unit_number + "</td>";
        new_row += "<td id='item_value_" + this.unit_number + "_value'>?</td>";
        if (this.cost == null){
            new_row += "<td id='item_value_" + this.unit_number + "_cost'>" + this.value + "</td>";
            new_row += "<td id='item_value_" + this.unit_number + "_earn'>?</td>";    
        } else{
            new_row += "<td id='item_value_" + this.unit_number + "_cost'>" + this.value + "</td>";
            new_row += "<td id='item_value_" + this.unit_number + "_earn'>" + this.earn + "</td>";                    
        }
        new_row += "</tr>";
        return new_row;
    }
    
}

class ItemList {
    constructor(){
        this.items = [];
        this.current_item = null;
    }

    add_item_value(item_value){
        this.items.push(item_value);
    }

    display_list(){
        for (const item_index in this.items) {
            var item_value = this.items[item_index];
            
            $('#item_earnings').append(item_value.display_row());
        }
    }
}



class BidItem {
    constructor(trader_id, price) {
        this.trader_id = trader_id;
        this.price = price;
        this.available = true;
    }

    make_unavailable(){
        this.available = false;
    }

    display_row(){
        var button_display = this.trader_id
        if (this.price != null){
            button_display += " - " + this.price; 
        }
        var new_button = "<button type='button'"
        if (this.price == null || !this.available){
            new_button += " disabled ";
        }
        new_button += " class='btn btn-primary  order-select-button' id='>" + button_display + "</button>";
        return new_button;
    }
    
}

class BidList {
    constructor(){
        this.items = [];
        this.current_item = null;
        this.selected_item = null;
    }

    add_bid_item(item_value){
        this.items.push(item_value);
    }

    display_list(){
        var new_button = "<button type='button' class='btn btn-primary order-select-button'>None</button>";        
        $('#available_trades').append(new_button  + " ");
        for (const item_index in this.items) {
            var item_value = this.items[item_index];
            $('#available_trades').append(item_value.display_row() + " ");
        }

        $('.order-select-button').click((event) => {
            console.log("CLICKED SOMETHING");

            });         
    }

    select_order(event){
        
    }

}



class MarketAgent {
    constructor() {
        console.log("Market Agent Instantiated");

        // Setup
        this.movement_window_active = false;
        this.order_window_active = false;
        this.trade_window_active = false;
        this.x_max = 7;
        this.y_max = 7;
   
        this.current_year = 1;
        this.total_year = 3;
        this.current_week = 1;
        this.total_week = 3;
        this.current_period = 1;
        this.total_period = 3;
        this.current_round = 1;
        this.total_round = 3;
        this.current_stage = "Move";
        this.earnings = 0;

        // Prep items
        this.item_list = new ItemList();
        this.item_list.add_item_value(new ItemValue(1, 97));
        this.item_list.add_item_value(new ItemValue(2, 105));
        this.item_list.add_item_value(new ItemValue(3, 110));
        this.item_list.display_list();
        
        // Prep purchases
        this.bid_list = new BidList();
        this.bid_list.add_bid_item(new BidItem(1, 25));
        this.bid_list.add_bid_item(new BidItem(2, null));
        this.bid_list.add_bid_item(new BidItem(3, 100));
        this.bid_list.add_bid_item(new BidItem(4, 99));
        this.bid_list.display_list();
        
        
        // Location
        this.x_location = 1;
        this.y_location = 1;
        this.location_history = [];

        this.prepare_actions();
        this.prepare_outlets();

        this.initialize_movement_buttons();
        this.initialize_numeric_order_entry();

        this.available_trades = [];

        this.display_move_result(this.x_location, this.y_location, -1, -1);

    

    }

    refresh_property(property_name, outlet_value, new_value){
        
        
        Object.defineProperty(this, outlet_value, 
            {set: (new_val) => {
                    $("#" + element_id).html(new_val);
                    delete this[property_name];
                    this[property_name] = new_val;
                    // this.set(outlet_value, new_val); 
                }
            });

    }

    property_setter_hook(element_id, outlet_value, new_val){
        console.log("jstartinga aflskfj");
        $("#" + element_id).html(new_val);
        delete this[outlet_value];
        this[outlet_value] = new_val;
        // this.set(outlet_value, new_val); 
        Object.defineProperty(this, outlet_value, 
            {
                get: () => { return new_val},
                set: (new_val) => this.property_setter_hook(element_id, outlet_value, new_val)
            });
    }


    prepare_outlets(){
        this.outlet_maps = {};
        $('[data-outlet-value]').each((item, element) => {
            // console.log(item)
            // console.log(this);
            // console.log(item);
            
            var element_id = element.id;
            var outlet_value = element.getAttribute("data-outlet-value");

            this.outlet_maps[outlet_value] = [this[outlet_value], element_id];

            if (this[outlet_value] != null){
                $("#" + element_id).html(this[outlet_value]);
            }
            var start_value = this[outlet_value];
            // this.refresh_property(outlet_value, element_id);
            Object.defineProperty(this, outlet_value, 
            {
                get: () => { return start_value},
                set: (new_val) => this.property_setter_hook(element_id, outlet_value, new_val)
            });

       });
    }


    prepare_actions(){
        $('[data-action-method]').each((item, element) => {
            console.log("Registering action");
            var target_action = element.getAttribute("data-action-method");
            var target_action_method = this[target_action];
            

            $(element).click((event) => {
                var target_action = event.currentTarget.getAttribute("data-action-method");
                var target_action_method = this[target_action];
                this[target_action]();

            }            
          );
        });
    }

    append_message(){
        var new_message = $("#append_message").val();

        var new_row = "<tr>"
        new_row += "<td colspan='2'>" + new_message + "</td>";
        new_row += "</tr>";
        $('#messages').append(new_row);

        $("#append_message").val("");

    }

    state_1(){
        this.enable_movement_buttons();
        this.disable_order_entry();
        this.disable_order_entry_value();
        this.disable_trades();
    }

    state_2(){
        this.disable_movement_buttons();
        this.enable_order_entry();
        this.disable_order_entry_value();
        this.disable_trades();
    }

    state_3(){
        this.disable_movement_buttons();
        this.disable_order_entry();
        this.disable_order_entry_value();
        this.disable_trades();
    }

    state_4(){
        this.disable_movement_buttons();
        this.disable_order_entry();
        this.enable_order_entry_value();
        this.enable_trades();
    }

    disable_movement_buttons(){
        $('.move_button').addClass('disabled-movement-button');
    }

    enable_movement_buttons(){
        $('.move_button').removeClass('disabled-movement-button');
    }


    enable_order_entry(){
        $('.order-entry').prop("disabled", false);
    }

    disable_order_entry(){
        $('.order-entry').prop("disabled", true);
    }

    enable_order_entry(){
        $('.order-entry').prop("disabled", false);
    }

    disable_order_entry(){
        $('.order-entry').prop("disabled", true);
    }


    enable_order_entry_value(){
        $('.order-entry-value').prop("disabled", false);
    }

    disable_order_entry_value(){
        $('.order-entry-value').prop("disabled", true);
    }

    initialize_numeric_order_entry(){
        $('.numeric').bind('keyup paste', () => {
            this.value = this.value.replace(/[^0-9]/g, '');
      });

      $('#order-entry input').on('change', (event) => {
          if ($("#order-entry input:checked").val() == "no_ask"){
            this.disable_order_entry_value();
            $("#order_entry_input").val("");
          }
          else {
            this.enable_order_entry_value();
          }
     });
    }

    move_direction(direction){
        var x_previous = this.x_location;
        var y_previous = this.y_location;

        var x_new = this.x_location;
        var y_new = this.y_location;
        console.log("MOVING...");
        console.log(this.x_location);

        switch (direction){
            case "move_nw":
                x_new = x_new - 1;
                y_new = y_new - 1;
                break;
            case "move_n":
                y_new = y_new - 1;
                break;
            case "move_ne":
                x_new = x_new + 1;
                y_new = y_new - 1;
                break;
            case "move_w":
                x_new = x_new - 1;
                break;
            case "move_e":
                x_new = x_new + 1;
                break;
            case "move_sw":
                x_new = x_new - 1;
                y_new = y_new + 1;
                break;
            case "move_s":
                y_new = y_new + 1;
                break;
            case "move_se":
                x_new = x_new + 1;
                y_new = y_new + 1;
                break;
            case "move_stay":
                break
        }
        console.log(x_new);
        console.log(y_new);
        if ((x_new <= this.x_max && x_new >= 0) && (y_new <= this.y_max && y_new >= 0)){            
            this.display_move_result(x_new, y_new, x_previous, y_previous);
        }        
    }

    display_move_result(x_new, y_new, x_previous,y_previous){
        let current_indicator = '<i class="bi bi-circle-fill"></i>';
        let blank_indicator = '<i class="bi bi-circle"></i>';
        var old_position = String(y_previous) + "-" + String(x_previous);
        $("#" + old_position).html(blank_indicator);

        var new_position = String(y_new) + "-" + String(x_new);
        $("#" + new_position).html(current_indicator);
        
        this.x_location = x_new;
        this.y_location = y_new;
    }

    initialize_movement_buttons(){
        $('.move_button').click((event) => {
            // console.log(event);
            console.log("MOVING");
            var id = $(event.currentTarget).attr('id');
            console.log(id);
            
            this.move_direction(id);
          });
    }

 
    add_trade(trade_type, player, value, status){
        var new_trade = {
            trade_type: trade_type,
            player: player,
            value: value,
            status: status
        }
        this.available_trades.push(new_trade);
    }

    enable_trades(){
        $('.trade-button').prop("disabled", false);
    }

    disable_trades(){
        $('.trade-button').prop("disabled", true);
    }


    display_trades(){
        let no_trade_button = '<button id="no_trade" type="button" class="btn btn-outline-primary trade-button">None</button>';
        $("#available_trades").append(no_trade_button);

        // Probably sort
        for (const trade_id in this.available_trades) {
            let trade = this.available_trades[trade_id];
            console.log(trade);
            console.log("Render trade");
        
            var id = trade.trade_type + "-" + trade.player + "-" + trade.value;
            var button_content = trade.player + " " + trade.value;
            var trade_button = '<button id="' + id + '" type="button" class="btn btn-outline-primary trade-button">' + button_content + '</button>';
            $("#available_trades").append(trade_button);

        }
    }


  }

console.log("Loading....");


//<i class="bi bi-circle"></i></td>
//<td id='0-1' classname="location-cell"><i class="bi bi-circle"></i>