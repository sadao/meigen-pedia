/*
 * jQuery Form Tips 1.2
 * By Manuel Boy (http://www.polargold.de)
 * Copyright (c) 2009 Manuel Boy
 * Licensed under the MIT License: http://www.opensource.org/licenses/mit-license.php
*/
jQuery.fn.formtips = function(options) {
	
	// handle options
	settings = jQuery.extend({
		tippedClass: "tipped"
	}, options);
	
	return this.each(function() {
		
		jQuery(this).each(function() {
			
			// prepare input elements an textareas
			var e = jQuery(this);
			
			// handle focus event
			jQuery(e).bind('focus', function() {
				var lv = jQuery(this).attr('title');
				if(jQuery(this).val() == lv) {
					jQuery(this).val('').removeClass(settings.tippedClass);
				}
				return false;
			});
			
			// handle blur event
			jQuery(e).bind('blur', function() {
				var lv = jQuery(this).attr('title');
				if(jQuery(this).val() == '') {
					jQuery(this).val(lv).addClass(settings.tippedClass);
				}
				return false;
			});
			
			// handle initial text
			var lv = jQuery(e).attr('title');
			if(jQuery(e).val() == '' || jQuery(e).val() == jQuery(this).attr('title')) {
				jQuery(e).val(lv).addClass(settings.tippedClass);
			} else {
				jQuery(e).removeClass(settings.tippedClass);
			}
			
		});
		
		// handle submit of forms (remove default value)
		if(jQuery('.' + settings.tippedClass, this).length > 0) {
			
			jQuery(this).submit(function() {
				
				// untip 'em
				jQuery('.' + settings.tippedClass, this).each(function() {
					var e = jQuery(this);
					var lv = jQuery(this).attr('title');
					if(jQuery(e).val() == lv) {
						jQuery(e).val('').removeClass(settings.tippedClass);
					}
				});
				
				return true;
			});
			
		}
		
	});
};